from django.http import HttpResponseRedirect
from django.urls import reverse
from .game import sudoku_board
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.template import loader
from django.utils import timezone
from .models import SavedSudoku


def generate_one_field(ngiven=23, randseed = None):
    """Generate a field with number of given cells ngiven.
    Field is represented as 9x9 matrix of integers (as Sudoku.state).
    Optionally randseed could be set, to achive reproducible fields."""
    sud = sudoku_board.Sudoku()
    if randseed is not None:
        sud.rnd_seed = randseed
    for i in range(3):
        sud.clear()
        #fill 3 3x3 squares with random permutations of 1..9
        sq1=list(range(1,10))
        sud.my_shuffle(sq1)
        sq2 = list(range(1, 10))
        sud.my_shuffle(sq2)
        sq3 = list(range(1, 10))
        sud.my_shuffle(sq3)

        sud.state=[
            [sq1[0], sq1[1], sq1[2], 0, 0, 0, 0, 0, 0],
            [sq1[3], sq1[4], sq1[5], 0, 0, 0, 0, 0, 0],
            [sq1[6], sq1[7], sq1[8], 0, 0, 0, 0, 0, 0],
            [0, 0, 0, sq2[0], sq2[1], sq2[2], 0, 0, 0],
            [0, 0, 0, sq2[3], sq2[4], sq2[5], 0, 0, 0],
            [0, 0, 0, sq2[6], sq2[7], sq2[8], 0, 0, 0],
            [0, 0, 0, 0, 0, 0, sq3[0], sq3[1], sq3[2]],
            [0, 0, 0, 0, 0, 0, sq3[3], sq3[4], sq3[5]],
            [0, 0, 0, 0, 0, 0, sq3[6], sq3[7], sq3[8]],
        ]
        #find first solution for this field, using randomization in solve_board
        solutions = sud.solve_board(True, True, 1)
        sud.state = sudoku_board.copy_state(solutions[0])

        #try to remove some cells and leave ngiven cells, using simulated annealing-like method
        board = sud.generate_board_annealing(ngiven, 500, False)

        #return the generated field, or None if generation wasn't successful
        return board

    return None

def replace_0_with_emptystr(sud):
    grid_emptycells = []
    size = sud.sudoku_dimensions_field
    for row in range(size):
        tmp = []
        for col in range(size):
            cell = sud.sudoku_state[row * size + col]
            if int(cell) > 0:
                tmp.append(cell)
            else:
                tmp.append("")

        grid_emptycells.append(tmp)

    return grid_emptycells

class SudokuListEntry:
    def __init__(self, id, grid):
        self.id = id
        self.grid = grid

def index_view(request):
        recent = SavedSudoku.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
        latest_sudoku_list = []
        for sud in recent:
            template = loader.get_template('sudoku/sudoku_board.html')
            context = {'sudoku_grid' : replace_0_with_emptystr(sud)}
            gr = template.render(context, request)
            le = SudokuListEntry(id=sud.id, grid = gr)
            latest_sudoku_list.append(le)

        return render(request,'sudoku/index.html', {'latest_sudoku_list' : latest_sudoku_list})

def generate(request, ngiven):
    if (21<=ngiven<=50):
        board = generate_one_field(ngiven)
    else:
        board = None

    if board is not None:
        grid_emptycells = []
        sudoku_state=""
        for row in board:
            tmp=[]
            for cell in row:
                sudoku_state = sudoku_state + str(cell)
                if cell > 0:
                    tmp.append(str(cell))
                else:
                    tmp.append("")
            grid_emptycells.append(tmp)

        context = {'sudoku_grid': grid_emptycells,
                   'dim_field': 9,
                   'dim_house': 3,
                   'sudoku_state': sudoku_state
                   }
    else:
        context ={'sudoku_grid':None}

    return render(request,'sudoku/generated.html', context)


def save(request,dim_field,dim_house,sudoku_state):
    sud = SavedSudoku(
                sudoku_dimensions_field = dim_field,
                sudoku_dimensions_house = dim_house,
                sudoku_state = sudoku_state,
                pub_date = timezone.now()
    )
    sud.save()
    return HttpResponseRedirect(reverse('sudoku:saved', args=(sud.id,)))


def saved(request, sudoku_id):
    sud = get_object_or_404(SavedSudoku, pk=sudoku_id)
    grid_emptycells = replace_0_with_emptystr(sud)

    context = {'sudoku_grid': grid_emptycells}

    return render(request,'sudoku/saved.html', context)