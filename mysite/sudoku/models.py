from django.db import models

class SavedSudoku(models.Model):
    sudoku_dimensions_field = models.IntegerField()
    sudoku_dimensions_house = models.IntegerField()
    sudoku_state = models.CharField(max_length=500)
    pub_date = models.DateTimeField()

    def __str__(self):
        size = self.sudoku_dimensions_field
        res = ""
        for row in range(size):
            for col in range(size):
                res = res + self.sudoku_state[row * size + col]
            res = res + "\n"

        return res

