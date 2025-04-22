def compare_series(series_list, dfs):
    from tools.llm.llm_tools import summarize_series
    summaries = [summarize_series(name, df) for name, df in zip(series_list, dfs)]
    return "\n\n".join(summaries)
