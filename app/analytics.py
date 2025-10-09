from typing import Optional, Dict, Any
import io
import os
from datetime import datetime

_HAS_PANDAS = True
_HAS_PLOTTING = True
try:
    import pandas as pd
except Exception:
    pd = None
    _HAS_PANDAS = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
except Exception:
    plt = None
    sns = None
    _HAS_PLOTTING = False

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
SURVEYS_CSV = os.path.join(DATA_DIR, "surveys.csv")


def _load_users_df():
    if not _HAS_PANDAS:
        return None
    if not os.path.exists(USERS_CSV):
        return pd.DataFrame()
    df = pd.read_csv(USERS_CSV)
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    return df


def _load_surveys_df():
    if not _HAS_PANDAS:
        return None
    if not os.path.exists(SURVEYS_CSV):
        return pd.DataFrame()
    df = pd.read_csv(SURVEYS_CSV)
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    # ensure numeric mood
    if 'mood' in df.columns:
        df['mood'] = pd.to_numeric(df['mood'], errors='coerce')
    return df


def analytics_summary() -> Dict[str, Any]:
    """Return a JSON-serializable summary of datasets: counts, basic stats and correlations."""
    users = _load_users_df()
    surveys = _load_surveys_df()

    if users is None or surveys is None:
        return {"error": "Missing dependencies: pandas is required for analytics. Install from requirements.txt."}

    summary: Dict[str, Any] = {}

    # Users summary
    summary['users'] = {
        'count': int(users.shape[0]) if not users.empty else 0,
        'first_created': users['created_at'].min().isoformat() if not users.empty and users['created_at'].notna().any() else None,
        'last_created': users['created_at'].max().isoformat() if not users.empty and users['created_at'].notna().any() else None
    }

    # Surveys summary
    if surveys.empty:
        summary['surveys'] = {'count': 0}
    else:
        surveys_stats = surveys['mood'].describe().to_dict()
        # convert numpy types
        surveys_stats_clean = {k: (float(v) if hasattr(v, 'item') else v) for k, v in surveys_stats.items()}
        summary['surveys'] = {
            'count': int(surveys.shape[0]),
            'mood_stats': surveys_stats_clean,
            'notes_present': int(surveys['notes'].notna().sum()) if 'notes' in surveys.columns else 0
        }

    # Correlations: if both dataframes present, correlate mood with user signup recency or counts
    try:
        if not surveys.empty and not users.empty:
            # compute avg mood per user
            mood_by_user = surveys.groupby('username')['mood'].mean()
            counts_by_user = surveys.groupby('username').size()
            merged = pd.DataFrame({'avg_mood': mood_by_user, 'count': counts_by_user})
            corr = merged.corr().to_dict()
            # simplify numpy types
            corr_clean = {k: {k2: (float(v2) if hasattr(v2, 'item') else v2) for k2, v2 in v.items()} for k, v in corr.items()}
            summary['correlations'] = corr_clean
    except Exception:
        summary['correlations'] = None

    # time series: average mood per day (last 90 days)
    try:
        if not surveys.empty and 'created_at' in surveys.columns:
            ts = surveys.set_index('created_at').resample('D')['mood'].mean().dropna()
            # keep last 90 days
            ts = ts.last('90D')
            summary['time_series'] = {d.strftime('%Y-%m-%d'): float(v) for d, v in ts.items()}
    except Exception:
        summary['time_series'] = None

    return summary


def avg_mood_by_group(group_by: str = 'username') -> Dict[str, Any]:
    """Compute average mood by a grouping column (default: username). Returns dict {group: avg_mood} sorted desc."""
    surveys = _load_surveys_df()
    if surveys is None:
        return {"error": "Missing dependencies: pandas is required for analytics."}
    if surveys.empty or group_by not in surveys.columns:
        return {}
    try:
        grouped = surveys.groupby(group_by)['mood'].mean().sort_values(ascending=False)
        return {str(k): float(v) for k, v in grouped.items()}
    except Exception:
        return {}


def alerts_risk(threshold: float = 3.0, window_days: int = 30) -> Dict[str, Any]:
    """Return alerts where mood <= threshold within the last window_days. Returns counts and items."""
    surveys = _load_surveys_df()
    if surveys is None:
        return {"error": "Missing dependencies: pandas is required for analytics."}
    if surveys.empty:
        return {"count": 0, "items": []}
    try:
        if 'created_at' in surveys.columns:
            cutoff = pd.Timestamp.now() - pd.Timedelta(days=window_days)
            recent = surveys[surveys['created_at'] >= cutoff]
        else:
            recent = surveys

        alerts = recent[recent['mood'] <= threshold]
        items = []
        for _, row in alerts.iterrows():
            items.append({
                'id': int(row.get('id', 0)),
                'user_id': int(row.get('user_id', 0)),
                'username': row.get('username'),
                'mood': float(row.get('mood') or 0),
                'notes': row.get('notes'),
                'created_at': pd.Timestamp(row.get('created_at')).isoformat() if row.get('created_at') is not None else None
            })

        return {'count': int(alerts.shape[0]), 'items': items}
    except Exception:
        return {'count': 0, 'items': []}


def evolution_time_series(days: int = 90) -> Dict[str, float]:
    """Return average mood per day for the last `days` days."""
    surveys = _load_surveys_df()
    if surveys is None:
        return {"error": "Missing dependencies: pandas is required for analytics."}
    if surveys.empty or 'created_at' not in surveys.columns:
        return {}
    try:
        ts = surveys.set_index('created_at').resample('D')['mood'].mean().dropna()
        ts = ts.last(f'{int(days)}D')
        return {d.strftime('%Y-%m-%d'): float(v) for d, v in ts.items()}
    except Exception:
        return {}


def generate_plot_png(plot_name: str) -> Optional[bytes]:
    """Return PNG bytes for supported plots.

    Supported:
    - 'mood_hist' : histogram of mood
    - 'mood_by_user' : boxplot of mood grouped by username (top 10 users)
    - 'mood_ts' : time series of average mood per day
    """
    surveys = _load_surveys_df()
    if surveys is None:
        return None
    if surveys.empty:
        return None

    buf = io.BytesIO()
    # Ensure plotting libs are available
    if not _HAS_PLOTTING:
        return None

    try:
        if plot_name == 'mood_hist':
            plt.figure(figsize=(8, 4))
            sns.histplot(surveys['mood'].dropna(), bins=10, kde=False)
            plt.title('Mood distribution')
            plt.xlabel('Mood')
            plt.ylabel('Count')
            plt.tight_layout()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return buf.read()

        if plot_name == 'mood_by_user':
            # boxplot per user - limit to top 10 users by count
            counts = surveys['username'].value_counts().head(10).index.tolist()
            df = surveys[surveys['username'].isin(counts)]
            plt.figure(figsize=(10, 6))
            sns.boxplot(x='username', y='mood', data=df)
            plt.xticks(rotation=45)
            plt.title('Mood by user (top 10)')
            plt.tight_layout()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return buf.read()

        if plot_name == 'mood_ts':
            if 'created_at' not in surveys.columns:
                return None
            ts = surveys.set_index('created_at').resample('D')['mood'].mean().dropna()
            ts = ts.last('90D')
            plt.figure(figsize=(10, 4))
            sns.lineplot(x=ts.index, y=ts.values)
            plt.title('Average mood per day (last 90 days)')
            plt.xlabel('Date')
            plt.ylabel('Average mood')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return buf.read()

    except Exception:
        return None

    return None
