from collections import Counter
from typing import Dict, List, Tuple
import numpy as np
from typing import Optional
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


def count_term_frequencies(df: pd.DataFrame, text_column: str, term_list: List[str]) -> pd.DataFrame:
    """
    Vectorize the text and count the frequencies of specific terms.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    text_column (str): The name of the column in df that contains the text to process.
    term_list (List[str]): A list of terms for which to calculate frequencies.

    Returns:
    term_freq_df (pd.DataFrame): A DataFrame where each column corresponds to a term in term_list and the values are the frequencies of the term in each document.
    """
    # Initialize CountVectorizer with the provided terms as the vocabulary
    count_vec = CountVectorizer(ngram_range=(1,2), vocabulary=term_list)

    # Fit and transform the text data
    X = count_vec.fit_transform(df[text_column]).toarray()

    # Create a DataFrame with the term frequencies
    term_freq_df = pd.DataFrame(X, columns=count_vec.get_feature_names_out())

    # For terms that contain a period, use straight string matching
    for term in term_list:
        if '.' in term:
            term_freq_df[term] = df[text_column].str.count(term)

    return term_freq_df


def generate_word_counts(df: pd.DataFrame, text_column: str, terms_list: List[str], list_name: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Process a DataFrame to calculate term frequencies and tokenize text.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    text_column (str): The name of the column in df that contains the text to process.
    terms_list (List[str]): A list of terms for which to calculate frequencies.
    list_name (str): A string to be used in naming the output columns.
    use_bigrams (bool): Whether to tokenize the text into bigrams. Defaults to False.

    Returns:
    df (pd.DataFrame): The original DataFrame, with additional columns for the lowercased text, tokenized text, token frequencies, and total tokens.
    count_df (pd.DataFrame): A copy of df, with additional columns for the actual and scaled frequencies of the terms in terms_list.
    terms_df (pd.DataFrame): A DataFrame containing the frequencies of the terms in terms_list.
    """
    if 'lower_text' not in df.columns:
        df['lower_text'] = df[text_column].str.lower()

    if 'total_tokens' not in df.columns:
        df['total_tokens'] = df['tokenized_text'].str.split(' ').str.len()
    
    count_df = count_term_frequencies(df, 'lower_text', terms_list)
    combined_df = pd.concat([df, count_df], axis=1)
    
    return combined_df

def process_data(file_path: str, text_column: str, date_column: str, terms_list: List, data_origin: str, title: str, term_type: str, term_mapping: bool, joined_term: Optional[str] = None):
    """
    Process the data and calculate term frequencies.

    Args:
        file_path (str): The path to the CSV file.
        text_column (str): The name of the column containing the text data.
        date_column (str): The name of the column containing the date data.
        terms_list (List): A list of terms to calculate frequencies for.
        data_origin (str): The origin of the data.
        title (str): The title of the data.
        id_column (str): The name of the column containing the ID data.
        term_type (str): The type of term data.
        term_mapping (bool): Whether to map term names for formatting variables.
        use_bigrams (bool): Whether to tokenize the text into bigrams.
        joined_term (str, optional): A term that we've searched for in multiple formats that we want to normalize into one term. Defaults to None.

    Returns:
        pd.DataFrame: The processed and calculated DataFrame.
    """
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Create a subset of the DataFrame that only includes rows where 'full_text' is not null
    subset_df = df[df[text_column].notna()]

    # Create a 'cleaned_conference_year' column by converting the 'conference_year' column to string and appending "-01-01"
    subset_df[f"cleaned_{date_column}"] = subset_df[date_column].astype(str) + "-01-01"

    # Convert the 'cleaned_conference_year' column to datetime format
    subset_df[f"cleaned_{date_column}"] = pd.to_datetime(subset_df[f"cleaned_{date_column}"])

    # Process the DataFrame to calculate term frequencies and tokenize text
    combined_df = generate_word_counts(subset_df, text_column, terms_list, term_type)
    # If a tool column is provided, create the 'finalized_tool' column
    if joined_term:
        plural_joined_term = joined_term + "s"
        combined_df[f'finalized_{joined_term}'] = np.where(combined_df[joined_term].notnull(), combined_df[joined_term], combined_df[plural_joined_term])
        combined_df = combined_df.drop(columns=[joined_term, plural_joined_term])
        combined_df = combined_df.rename(columns={f"finalized_{joined_term}": joined_term})

    id_vars_columns = df.columns.tolist()
    melted_combined_df = pd.melt(combined_df, id_vars=id_vars_columns, var_name=term_type, value_name='counts')
    melted_combined_df['scaled_counts'] = melted_combined_df['counts'] / melted_combined_df['total_tokens']
    
    # If term mapping is enabled, map the terms
    if term_mapping:
        # Create a mapping from lowercase tool name to the correct name
        term_mapping = {term.lower(): term for term in terms_list}
        melted_combined_df[term_type] = melted_combined_df[term_type].replace(term_mapping)

    # Group the DataFrame by 'cleaned_conference_year' and 'tool' and calculate the sum of 'counts' for each group, then reset the index
    summed_df = melted_combined_df.groupby([f"cleaned_{date_column}", term_type]).counts.sum().reset_index()

    # Group the DataFrame by 'cleaned_conference_year' and 'tool' and calculate the sum of 'scaled_counts' for each group, then reset the index
    scaled_df = melted_combined_df.groupby([f"cleaned_{date_column}", term_type]).scaled_counts.sum().reset_index()

    # Group the DataFrame by 'cleaned_conference_year' and calculate the sum of 'total_tokens' for each group, then reset the index
    total_tokens_df = melted_combined_df.groupby([f"cleaned_{date_column}", term_type]).total_tokens.sum().reset_index()

    # Merge the grouped DataFrames
    grouped_df = pd.merge(summed_df, scaled_df, on=[f"cleaned_{date_column}", term_type])

    # Merge the grouped DataFrame with the total tokens DataFrame
    grouped_df = pd.merge(grouped_df, total_tokens_df, on=[f"cleaned_{date_column}", term_type])

    # Multiply the 'scaled_counts' column by 100
    grouped_df.scaled_counts = grouped_df.scaled_counts * 100

    # Rename the 'cleaned_conference_year' column to 'date'
    grouped_df = grouped_df.rename(columns={f"cleaned_{date_column}": "date"})

    # Add a 'data_origin' column with the value 'Index of DH Conferences'
    grouped_df["data_origin"] = data_origin

    # Add a 'title' column with the value 'Index of DH Conferences by Weingart et al (2023)'
    grouped_df["title"] = title

    return grouped_df