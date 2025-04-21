import json
import streamlit as st

class BookClassroom:
    
    def __init__(self):
        # Initializes a new book collection with an empty list and set up file storage
        if 'book_list' not in st.session_state:
            st.session_state.book_list = []
        self.storage_file = "books_data.json"
        self.read_from_file()

    def read_from_file(self):
        # Loads books from json file into memory
        try:
            with open(self.storage_file, 'r') as file:
                content = file.read().strip()
                if content:  # Check if the file is not empty
                    st.session_state.book_list = json.loads(content)
                else:
                    st.session_state.book_list = []
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or is not valid JSON, keep empty book list
            st.session_state.book_list = []

    def save_to_file(self):
        # Store the current book collection to a json file for permanent storage.
        with open(self.storage_file, "w") as file:
            json.dump(st.session_state.book_list, file)
            
    def create_new_book(self, book_title, book_author, publication_year, book_genre, has_read_book):
        # Add new books to the collection
        new_book = {
            "title" : book_title,
            "author" : book_author,
            "publication_year": publication_year,
            "genre": book_genre,
            "has_read_book": has_read_book
        }
        
        st.session_state.book_list.append(new_book)
        self.save_to_file()
        return True

    def delete_book(self, book_title):
        # Remove a book from the collection using it's title.
        for book in st.session_state.book_list:
            if book["title"].lower() == book_title.lower():
                st.session_state.book_list.remove(book)
                self.save_to_file()
                return True
        return False

    def find_book(self, search_text):
        # Search for books in the collection by title or author name.
        found_books = [
            book
            for book in st.session_state.book_list
            if search_text.lower() in book["title"].lower()
            or search_text.lower() in book["author"].lower()
        ]
        return found_books
    
    def update_book(self, old_title, new_title, new_author, new_year, new_genre, has_read):
        # Modify the details of an existing book in the collection.
        for book in st.session_state.book_list:
            if book["title"].lower() == old_title.lower():
                book["title"] = new_title if new_title else book["title"]
                book["author"] = new_author if new_author else book["author"]
                book["publication_year"] = new_year if new_year else book["publication_year"]
                book["genre"] = new_genre if new_genre else book["genre"]
                book["has_read_book"] = has_read
                self.save_to_file()
                return True
        return False

    def show_reading_progress(self):
        # Calculate reading statistics
        total_books = len(st.session_state.book_list)
        if total_books == 0:
            return 0, 0, 0
            
        books_read = sum(1 for book in st.session_state.book_list if book["has_read_book"])
        percentage = (books_read / total_books) * 100 if total_books > 0 else 0
        return total_books, books_read, percentage

# Streamlit UI
def main():
    st.set_page_config(page_title="Personal Library Manager", page_icon="📚")
    st.title("📚 Personal Library Manager")
    
    # Initialize the book manager
    manager = BookClassroom()
    
    # Sidebar for navigation
    menu = st.sidebar.selectbox(
        "Menu", 
        ["View All Books", "Add New Book", "Search Books", "Update Book", "Delete Book", "Reading Progress"]
    )
    
    # View all books
    if menu == "View All Books":
        st.header("Your Book Collection")
        if not st.session_state.book_list:
            st.info("Your collection is empty.")
        else:
            for i, book in enumerate(st.session_state.book_list, 1):
                reading_status = "Read" if book["has_read_book"] else "Unread"
                st.write(f"{i}. **{book['title']}** by {book['author']} ({book['publication_year']}) - {book['genre']} - {reading_status}")
    
    # Add new book
    elif menu == "Add New Book":
        st.header("Add a New Book")
        with st.form("add_book_form"):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            year = st.text_input("Publication Year")
            genre = st.text_input("Genre")
            has_read = st.checkbox("I have read this book")
            
            submit_button = st.form_submit_button("Add Book")
            if submit_button and title and author:
                if manager.create_new_book(title, author, year, genre, has_read):
                    st.success("Book added successfully!")
                else:
                    st.error("Failed to add book.")
    
    # Search books
    elif menu == "Search Books":
        st.header("Search Books")
        search_term = st.text_input("Enter search term")
        if search_term:
            results = manager.find_book(search_term)
            if results:
                st.subheader(f"Found {len(results)} book(s):")
                for i, book in enumerate(results, 1):
                    reading_status = "Read" if book["has_read_book"] else "Unread"
                    st.write(f"{i}. **{book['title']}** by {book['author']} ({book['publication_year']}) - {book['genre']} - {reading_status}")
            else:
                st.info("No matching books found.")
    
    # Update book
    elif menu == "Update Book":
        st.header("Update Book Details")
        if not st.session_state.book_list:
            st.info("Your collection is empty.")
        else:
            book_titles = [book["title"] for book in st.session_state.book_list]
            selected_book = st.selectbox("Select a book to update", book_titles)
            
            if selected_book:
                # Find the selected book
                for book in st.session_state.book_list:
                    if book["title"] == selected_book:
                        with st.form("update_book_form"):
                            st.write("Leave blank to keep existing value.")
                            new_title = st.text_input("New Title", book["title"])
                            new_author = st.text_input("New Author", book["author"])
                            new_year = st.text_input("New Publication Year", book["publication_year"])
                            new_genre = st.text_input("New Genre", book["genre"])
                            new_has_read = st.checkbox("I have read this book", book["has_read_book"])
                            
                            update_button = st.form_submit_button("Update Book")
                            if update_button:
                                if manager.update_book(selected_book, new_title, new_author, new_year, new_genre, new_has_read):
                                    st.success("Book updated successfully!")
                                else:
                                    st.error("Failed to update book.")
    
    # Delete book
    elif menu == "Delete Book":
        st.header("Delete a Book")
        if not st.session_state.book_list:
            st.info("Your collection is empty.")
        else:
            book_titles = [book["title"] for book in st.session_state.book_list]
            selected_book = st.selectbox("Select a book to delete", book_titles)
            
            if selected_book and st.button("Delete Book"):
                if manager.delete_book(selected_book):
                    st.success("Book deleted successfully!")
                else:
                    st.error("Failed to delete book.")
    
    # Reading progress
    elif menu == "Reading Progress":
        st.header("Your Reading Progress")
        total, read, percentage = manager.show_reading_progress()
        
        if total == 0:
            st.info("Your collection is empty.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Books", total)
            with col2:
                st.metric("Books Read", read)
            with col3:
                st.metric("Completion", f"{percentage:.1f}%")
            
            # Progress bar
            st.progress(percentage/100)

if __name__ == "__main__":
    main()
