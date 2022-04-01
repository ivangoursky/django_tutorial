from django.db import models

class SudokuBlogUser(models.Model):
    loginname = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    is_registered_user = models.BooleanField()
    password_hash = models.CharField(max_length=100)

    def __str__(self):
        return self.loginname

class SavedSudoku(models.Model):
    sudoku_dimensions_field = models.IntegerField()
    sudoku_dimensions_house = models.IntegerField()
    sudoku_state = models.CharField(max_length=500)
    pub_date = models.DateTimeField()
    sudoku_user = models.ForeignKey(SudokuBlogUser, on_delete=models.CASCADE)

    def __str__(self):
        size = self.sudoku_dimensions_field
        res = ""
        for row in range(size):
            for col in range(size):
                res = res + self.sudoku_state[row * size + col]
            res = res + "\n"

        return res

class SudokuComment(models.Model):
    saved_sudoku = models.ForeignKey(SavedSudoku, on_delete=models.CASCADE)
    comment_user = models.ForeignKey(SudokuBlogUser, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=1000)
    pub_date = models.DateTimeField()

    def __str__(self):
        return "%s at %s: %s" % (self.comment_user.loginname, self.pub_date, self.comment_text)

class SudokuBlogUserSession(models.Model):
    sudoku_user = models.ForeignKey(SudokuBlogUser, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    expires_at = models.DateTimeField()