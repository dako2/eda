
# Data Interface Tool for Ouma's Amazing Flowers
def query_book_content(query):
    '''
    A simple function to simulate responses based on queries about the book 'Ouma's Amazing Flowers'.
    This is a placeholder for actual PDF content extraction and RAG-based querying.
    '''
    query = query.lower()
    if 'summary' in query or 'about' in query:
        return ("The book 'Ouma's Amazing Flowers' by Laurie Janey, Amber Tak, and Roulé le Roux "
                "is a children's story about Ouma's flowers that bring joy to everyone passing by. "
                "The story emphasizes protecting the flowers so Ouma can enjoy them and suggests planting more flowers together.")
    elif 'title' in query:
        return "The title of the book is 'Ouma's Amazing Flowers'."
    elif 'author' in query or 'authors' in query:
        return "The authors are Laurie Janey, Amber Tak, and Roulé le Roux."
    elif 'theme' in query or 'message' in query:
        return "A recurring theme is protecting the flowers so Ouma can enjoy seeing them, and there is a suggestion to plant more flowers together."
    else:
        return "I'm not sure how to answer that query. Please ask something related to the content of 'Ouma's Amazing Flowers'."

# Example usage
if __name__ == '__main__':
    sample_query = 'Can you summarize the book?'
    response = query_book_content(sample_query)
    print(f'Query: {sample_query}')
    print(f'Response: {response}')
