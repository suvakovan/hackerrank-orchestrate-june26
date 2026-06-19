def evaluate_history(user_id, history_df):
    """
    Retrieves user history flags from the user_history.csv dataframe
    Returns risk_flags (list or string)
    """
    # Look up user_id in the dataframe
    user_row = history_df[history_df['user_id'] == user_id]
    
    if not user_row.empty:
        flags = user_row.iloc[0]['history_flags']
        return flags if flags else "none"
    return "none"
