import streamlit as st
import json
import os
import pandas as pd  # For tabular display and data analysis
import plotly.express as px  # For visualization

# File to store library data
LIBRARY_FILE = "library.json"

# Custom CSS for modern UI - Improved
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
    }
    h1, h2, h3 {
        color: #2e86c1;
    }
    .stButton button {
        background-color: #2e86c1;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        margin-bottom: 5px; /* Add spacing below buttons */
    }
    .stButton button:hover {
        background-color: #1b4f72;
    }
    .stTextInput input, .stNumberInput input, .stCheckbox label {
        font-size: 16px;
    }
    .stSidebar {
        background-color: #2e86c1;
        color: white;
    }
    .stSidebar .sidebar-content {
        padding: 20px;
    }
    .stSidebar .sidebar-content h2 {
        color: white;
    }
    .book-details {
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 10px;
        background-color: white; /* Make book details stand out */
    }

    /* Style for the data editor */
    div[data-baseweb="data-grid"] {
        border: 1px solid #ccc;
        border-radius: 5px;
        overflow: hidden; /* Hide scrollbars */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize the library
def load_library():
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, "r") as file:
            return json.load(file)
    return []

def save_library(library):
    with open(LIBRARY_FILE, "w") as file:
        json.dump(library, file)

# Add a book
def add_book(library):
    st.subheader("📖 Add a Book")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title", placeholder="Enter title...")  # Placeholders
        author = st.text_input("Author", placeholder="Enter author...")
    with col2:
        year = st.number_input("Publication Year", min_value=1000, max_value=2024, step=1) # Enforce reasonable year
        genre = st.text_input("Genre", placeholder="Enter genre...")
    read_status = st.checkbox("Read Status (Checked if read)")
    if st.button("Add Book"):
        if title and author and year and genre:
            book = {
                "title": title,
                "author": author,
                "year": int(year),  # Ensure year is saved as an integer
                "genre": genre,
                "read_status": read_status
            }
            library.append(book)
            save_library(library)
            st.success(f"✅ Book '{title}' by {author} added successfully!")  # More informative success message
        else:
            st.error("❌ Please fill in all fields.")

# Remove a book
def remove_book(library):
    st.subheader("🗑️ Remove a Book")
    title_to_remove = st.text_input("Enter the title of the book to remove", placeholder="Enter title...")
    if st.button("Remove Book"):
        initial_count = len(library)
        library[:] = [book for book in library if book["title"].lower() != title_to_remove.lower()]
        if len(library) < initial_count:
            save_library(library)
            st.success(f"✅ Book '{title_to_remove}' removed successfully!")
        else:
            st.error("❌ Book not found.")

# Search for a book
def search_books(library):
    st.subheader("🔍 Search for a Book")
    search_query = st.text_input("Enter title or author to search", placeholder="Enter search term...")
    if search_query:
        results = [
            book for book in library
            if search_query.lower() in book["title"].lower() or search_query.lower() in book["author"].lower()
        ]
        if results:
            st.write("### Search Results:")
            for book in results:
                st.markdown(f"""
                <div class="book-details">
                **Title:** {book['title']}<br>
                **Author:** {book['author']}<br>
                **Year:** {book['year']}<br>
                **Genre:** {book['genre']}<br>
                **Read:** {'✅ Yes' if book['read_status'] else '❌ No'}
                </div>
                """, unsafe_allow_html=True)  # Use HTML for styling
        else:
            st.info("No matching books found.") # Use st.info for better visual cue

# Display all books - Now as a Table!
def display_books(library):
    st.subheader("📚 All Books")
    if library:
        df = pd.DataFrame(library)  # Convert to Pandas DataFrame
        # Reorder columns for better readability
        df = df[['title', 'author', 'year', 'genre', 'read_status']]
        st.dataframe(df, use_container_width=True)  # Display DataFrame
    else:
        st.info("No books in the library yet. Add some!") # Use st.info

# Display statistics - Enhanced with visualizations
def display_statistics(library):
    st.subheader("📊 Library Statistics")
    total_books = len(library)
    read_books = sum(1 for book in library if book["read_status"])
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0

    col1, col2 = st.columns(2)  # Display metrics in two columns
    with col1:
        st.metric("Total Books", total_books)
    with col2:
        st.metric("Percentage Read", f"{percentage_read:.2f}%")

    # Genre Analysis (Bar Chart)
    if library:
        genre_counts = pd.Series([book['genre'] for book in library]).value_counts()
        fig = px.bar(x=genre_counts.index, y=genre_counts.values,
                     labels={'x': 'Genre', 'y': 'Number of Books'},
                     title='Books per Genre')
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Add books to see statistics.")

# Export library to a text file
def export_library(library):
    st.subheader("📤 Export Library to Text File")
    if st.button("Export Library"):
        try:
            with open("library.txt", "w", encoding="utf-8") as file:  # Explicit encoding for wider character support
                for book in library:
                    file.write(f"Title: {book['title']}\n")
                    file.write(f"Author: {book['author']}\n")
                    file.write(f"Year: {book['year']}\n")
                    file.write(f"Genre: {book['genre']}\n")
                    file.write(f"Read: {'Yes' if book['read_status'] else 'No'}\n")
                    file.write("-" * 30 + "\n")
            st.success("✅ Library exported to 'library.txt' successfully!")
        except Exception as e:
            st.error(f"❌ Error exporting library: {e}")

# Import library from a text file
def import_library():
    st.subheader("📥 Import Library from Text File")
    uploaded_file = st.file_uploader("Upload 'library.txt'", type=["txt"])
    if uploaded_file is not None:
        try:
            lines = uploaded_file.getvalue().decode("utf-8").splitlines()
            library = []
            book = {}
            for line in lines:
                if line.startswith("Title:"):
                    book["title"] = line.replace("Title: ", "").strip()
                elif line.startswith("Author:"):
                    book["author"] = line.replace("Author: ", "").strip()
                elif line.startswith("Year:"):
                    year_str = line.replace("Year: ", "").strip()
                    try:
                        book["year"] = int(year_str)
                    except ValueError:
                        st.warning(f"Invalid year format in line: {line}. Skipping year.")
                        book["year"] = None # or a default value like 0
                elif line.startswith("Genre:"):
                    book["genre"] = line.replace("Genre: ", "").strip()
                elif line.startswith("Read:"):
                    book["read_status"] = line.replace("Read: ", "").strip() == "Yes"
                    library.append(book)
                    book = {}
            save_library(library)
            st.success("✅ Library imported from 'library.txt' successfully!")
            return library
        except Exception as e:
            st.error(f"❌ Error importing library: {e}")
            return None
    return None

# Function to clear the library (Confirmation Dialog)
def clear_library(library):
    st.subheader("💣 Clear Library")
    if st.button("Clear All Books (Warning: This action is irreversible!)"):
        if st.session_state.get("confirm_clear", False):
            library.clear()
            save_library(library)
            st.success("✅ Library cleared successfully!")
            st.session_state["confirm_clear"] = False # Reset confirmation state
        else:
            st.warning("Are you sure you want to clear the entire library? This cannot be undone. Press the button again to confirm.")
            st.session_state["confirm_clear"] = True # Set confirmation state

# Main function
def main():
    st.title("📚 Personal Library Manager")
    library = load_library()

    # Initialize session state for confirmation dialog
    if "confirm_clear" not in st.session_state:
        st.session_state["confirm_clear"] = False

    # Sidebar menu - Reordered for Logical Flow
    st.sidebar.title("Menu")
    menu = [
        "Display All Books",
        "Add a Book",
        "Search for a Book",
        "Remove a Book",
        "Display Statistics",
        "Import Library",
        "Export Library",
        "Clear Library",  # Add the clear library option
        "Exit"
    ]
    choice = st.sidebar.radio("Choose an option", menu)

    if choice == "Add a Book":
        add_book(library)
    elif choice == "Remove a Book":
        remove_book(library)
    elif choice == "Search for a Book":
        search_books(library)
    elif choice == "Display All Books":
        display_books(library)
    elif choice == "Display Statistics":
        display_statistics(library)
    elif choice == "Export Library":
        export_library(library)
    elif choice == "Import Library":
        imported_library = import_library()
        if imported_library:
            library = imported_library
    elif choice == "Clear Library":
        clear_library(library) # Call the function to clear the library with confirmation
    elif choice == "Exit":
        st.write("Thank you for using the Personal Library Manager! 👋")
        save_library(library)
        st.stop()


if __name__ == "__main__":
    main()