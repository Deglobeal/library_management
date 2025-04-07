class BookCart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("book_cart", {})
        self.cart = cart
        
    def add(self, book_id):
        if str(book_id) not in self.cart:
            self.cart[str(book_id)] = {'selected': {}}
            self.save()
            
    def remove(self, book_id):
        if str(book_id) in self.cart:
            del self.cart[str(book_id)]
            self.save()
            
    def toggle(self, book_id):
        if str(book_id) in self.cart:
            self.remove(book_id)
            
        else:
            self.add(book_id)
            return str(book_id) in self.cart
        
    def get_selected(self):
        selected_books = []
        for book_id, book in self.cart.items():
            if book['selected']:
                selected_books.append(book_id)
        return selected_books
    
    def save(self):
        self.session.modified = True
        self.session['book_cart'] = self.cart
        
