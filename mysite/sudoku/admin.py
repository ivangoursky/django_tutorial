from django.contrib import admin

from django.contrib import admin

from .models import SavedSudoku, SudokuBlogUser, SudokuComment

admin.site.register(SavedSudoku)
admin.site.register(SudokuBlogUser)
admin.site.register(SudokuComment)
