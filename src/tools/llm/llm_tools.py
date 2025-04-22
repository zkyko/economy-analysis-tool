def compare_series(series_list, dfs):
    from tools.llm.llm_tools import summarize_series
    summaries = [summarize_series(name, df) for name, df in zip(series_list, dfs)]
    return "\n\n".join(summaries)

def summarize_series(series_name, df, time_range=None, desc=None):
    if df.empty:
        return f"No data available for {series_name}."
    latest = df.iloc[-1]
    msg = f"**{series_name}**\n\nLatest value: **{latest['value']:.2f}** on {latest['date'].date()}"
    if time_range:
        msg += f"\nTime range: {time_range}"
    if desc:
        msg += f"\nDescription: {desc}"
    if len(df) > 12:
        prev = df.iloc[-13]
        pct = (latest['value'] - prev['value']) / abs(prev['value']) * 100 if prev['value'] != 0 else float('nan')
        msg += f"\nYoY change: **{pct:.2f}%**"
    msg += f"\n\nMin: {df['value'].min():.2f} | Max: {df['value'].max():.2f}"
    return msg
