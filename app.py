import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import seaborn as sns
import requests

# I uploaded the dataset to my personal website to download from because it is too large to fit on Github
url = "https://www.nikilshyamsunder.com/_files/ugd/3c41f5_75a24860301147a080fbf1dffa8503e7.csv?dn=repository_data.csv"

# Set Streamlit page configuration
st.set_page_config(
    page_title="GitHub Repository Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('Beacon Dashboard: Github Repository Dataset')

# Load the dataset
#df = pd.read_csv('data/repository_data.csv')
df = pd.read_csv(url)

# Display 3 Important Metrics
num_rows = df.shape[0]
most_popular_language = df['primary_language'].mode().iloc[0]
most_popular_license = df['licence'].mode().iloc[0]
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Number of Repositories", "{:,}".format(num_rows))
with col2:
    st.metric("Most Popular Language", most_popular_language)
with col3:
    st.metric("Most Popular License", most_popular_license)

# Analysis
# 1. Popular Language
language_counts = df['primary_language'].value_counts()
language_counts = pd.DataFrame(language_counts.iloc[:10]).reset_index() #take the top 10 as new DataFrame

# convert frequencies to relative frequencies
def rel_freq(string):
    return int(string) / num_rows
language_counts['Relative Frequency'] = language_counts['count'].apply(rel_freq)
language_counts.columns = ['Primary Language', 'count', 'Relative Frequency']

with col1:
    #st.header('Top 10 Most Popular Primary Languages for Github Repositoriess')
    st.write(alt.Chart(language_counts, title='Top 10 Most Popular Primary Languages for Repos').mark_bar().encode(  # plot
        x=alt.X('Primary Language', sort=None),
        y='Relative Frequency'
    ))

# 2. Second Most Popular Language
def string_to_list(string):
    if type(string) == str:
        lst = string.strip('][').split(', ')
        for i in range(len(lst)):
            lst[i] = lst[i][1:-1] # remove beginning and ending quotes
        return lst


languages_used = df['languages_used'].apply(string_to_list) # converts column into actual python lists

# Extract the second language from each list, if it exists
second_languages = languages_used.apply(lambda x: x[1] if x is not None and len(x) > 1 else None)

# Filter out None values and count occurrences
second_language_counts = second_languages.value_counts()
second_language_counts = pd.DataFrame(second_language_counts.iloc[:10]).reset_index() #take the top 10 as new DataFrame

# convert frequencies to relative frequencies
second_language_counts['Relative Frequency'] = second_language_counts['count'].apply(rel_freq)
second_language_counts.columns = ['Secondary Language', 'count', 'Relative Frequency']

#print(second_language_counts.columns)
with col2: # plot
    st.write(alt.Chart(second_language_counts, title="Top 10 Most Popular Secondary Languages for Repos").mark_bar().encode(
        x=alt.X('Secondary Language', sort=None),
        y='Relative Frequency',
        color=alt.value('red')
    ))

# 3. Language-Pairs Bar Graph
# Apply function to convert 'languages_used' into lists
df['languages_used'] = df['languages_used'].apply(string_to_list)

# Extract the second language from each list, if it exists
df['second_language'] = df['languages_used'].apply(lambda x: x[1] if x is not None and len(x) > 1 else None)
df = df[df['second_language'].notnull()]

# Shorten "Jupyter Notebook" to "Jupyter" for space economy
df['primary_language'] = df['primary_language'].replace('Jupyter Notebook', 'Jupyter')

# Create pairs of primary and secondary languages
df['language_pairs'] = df.apply(lambda row: (row['primary_language'], row['second_language']), axis=1)

# Count occurrences of each pair
language_pair_counts = df['language_pairs'].value_counts().head(10)  # Adjust the number to display as needed
language_pair_counts = language_pair_counts.reset_index()
with col3:
    st.write(alt.Chart(language_pair_counts, title="Top 10 Most Primary-Secondary Language Pairs").mark_bar().encode(
            x=alt.X('language_pairs', sort=None),
            y='count',
            color=alt.value('purple')
        ))

    
# 3.5. Analysis
with col2:
    st.write('The data show that JavaScript and Python hold strong positions as the two most popular languages used on GitHub as the primary language for a repository. While Python is more often used in repositories alone or in shell scripts, JavaScript is most commonly used in complement to HTML, CSS, TypeScript, and other Web Application Technologies.\n\nRuby was the most popular language in the early years of GitHub, but JavaScript and Python have become much more popular over the past decade. While JavaScript makes up a greater proportion of the total dataset, since 2018 Python-based repositories have become dominant--possibly because of the rise of Machine Learning using Python.\n\n\n\n\n\n\n')

# 4. Number of Repos Created Per Month Over Time
df['created_at'] = pd.to_datetime(df['created_at'])
month_freq = df.set_index('created_at').resample('M').size() # aggregate number of repos made per month
month_freq = month_freq.iloc[:-1] # remove the last month because incomplete

with col1:
    st.subheader('Number of Repos Created Per Month')
    st.line_chart(month_freq) # plot

# 5. Most Popular Primary Language Year to Year
# Convert 'created_at' to datetime and extract the year
df = pd.read_csv('data/repository_data.csv')
df['year'] = pd.to_datetime(df['created_at']).dt.year

# Group by year and primary_language, count occurrences
language_counts_by_year = df.groupby(['year', 'primary_language']).size().reset_index(name='count')

# For each year, find the language with the highest count
most_popular_languages_by_year = language_counts_by_year.sort_values(['year', 'count'], ascending=[True, False]).drop_duplicates('year')
print(most_popular_languages_by_year)

# Pivot for easy plotting
pivot_data = most_popular_languages_by_year.pivot(index='year', columns='primary_language', values='count').fillna(0)
print(pivot_data)

plt.figure(figsize=(3, 3))
sns.heatmap(pivot_data, annot=True, cmap="YlGnBu", fmt='g')
#plt.title('Most Popular Primary Language Each Year')
plt.ylabel('Year')
plt.xlabel('Primary Language')

with col3:
    st.subheader('Most Popular Primary Language Each Year')
    st.pyplot(plt.gcf())


# Display the full dataset
#st.dataframe(df)

# 6. Data itself
st.header('In-Depth Data')
st.dataframe(df.iloc[:500000]) # only giving half the dataset, because too large to fully display in streamlit

