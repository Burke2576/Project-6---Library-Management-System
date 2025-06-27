class Book:
    def __init__(self, book_ID, title, author, genre, publication_year, available=True):
        self.book_ID = book_ID
        self.title = title
        self.author = author
        self.genre = genre
        self.publication_year = publication_year
        self.available = available     

    def __repr__(self):
        return f"Book(ID={self.book_ID}, Title='{self.title}', Available={self.available})"

    def __eq__(self, other):
        return self.book_ID == other.book_ID

    def __lt__(self, other):
        return self.title < other.title
