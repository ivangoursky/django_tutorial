from django.http import HttpResponseRedirect
from django.urls import reverse
from .game import sudoku_board
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.template import loader
from django.utils import timezone
from .models import SavedSudoku, SudokuComment, SudokuBlogUser
from .user import *


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

class SudokuCell:
    def __init__(self, cell_text, cell_style):
        self.cell_text = cell_text
        self.cell_style = cell_style

def prepare_grid(sud):
    grid_emptycells = []
    size = sud.sudoku_dimensions_field
    house_size = sud.sudoku_dimensions_house
    for row in range(size):
        tmp = []
        for col in range(size):
            cell_text = sud.sudoku_state[row * size + col]
            if cell_text == "0":
                cell_text = ""
            style=""
            if row % house_size == 0:
                style = style + "upper"
            if col % house_size == 0:
                style = style + "left"

            if style=="":
                style="usual"

            tmp.append(SudokuCell(cell_text, style))

        grid_emptycells.append(tmp)

    return grid_emptycells


def add_header_context(request, context):
    user = get_logged_in_user(request)
    if user is not None:
        context['logged_in_user'] = user


class SudokuListEntry:
    def __init__(self, id, grid):
        self.id = id
        self.grid = grid

def index_view(request):
        recent = SavedSudoku.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
        latest_sudoku_list = []
        for sud in recent:
            template = loader.get_template('sudoku/sudoku_board.html')
            context = get_savedsudoku_context(sud.id)
            gr = template.render(context, request)
            le = SudokuListEntry(id=sud.id, grid = gr)
            latest_sudoku_list.append(le)

        ngiven = range(21,51)
        ngiven_byrow = []
        tmp = []
        for i in range(len(ngiven)):
            tmp.append(ngiven[i])
            if i % 5 == 4:
                ngiven_byrow.append(tmp)
                tmp = []

        if len(tmp) > 0:
            ngiven_byrow.append(tmp)

        context = {'latest_sudoku_list' : latest_sudoku_list, 'ngiven': ngiven_byrow}
        add_header_context(request, context)
        return render(request,'sudoku/index.html', context)

def generate(request, ngiven):
    if (21<=ngiven<=50):
        board = generate_one_field(ngiven)
    else:
        board = None

    if board is not None:
        sudoku_state=""
        for row in board:
            for cell in row:
                sudoku_state = sudoku_state + str(cell)

        tmp_sud = SavedSudoku(
            sudoku_dimensions_field=9,
            sudoku_dimensions_house = 3,
            sudoku_state = sudoku_state,
            pub_date = timezone.now(),
            sudoku_user = get_anonymous_user()
        )
        context = get_sudoku_context(tmp_sud,temp=True)
        context['dim_field'] = 9
        context['dim_house'] = 3
        context['sudoku_state'] = sudoku_state
    else:
        context ={'sudoku_grid':None}

    add_header_context(request, context)
    return render(request,'sudoku/generated.html', context)


def save(request,dim_field,dim_house,sudoku_state):
    usr = get_logged_in_user(request)
    if usr is None:
        usr = get_anonymous_user()
    sud = SavedSudoku(
                sudoku_dimensions_field = dim_field,
                sudoku_dimensions_house = dim_house,
                sudoku_state = sudoku_state,
                pub_date = timezone.now(),
                sudoku_user = usr
    )
    sud.save()
    return HttpResponseRedirect(reverse('sudoku:saved', args=(sud.id,)))

def get_sudoku_context(sud, temp=False):
    grid_emptycells = prepare_grid(sud)
    if temp:
        sudoku_id = None
        comments = None
    else:
        sudoku_id = sud.id
        comments = sud.sudokucomment_set.filter(saved_sudoku_id=sudoku_id)

    context = {
        'sudoku_grid': grid_emptycells,
        'sudoku_id': sudoku_id,
        'sudoku_user': sud.sudoku_user,
        'sudoku_date': sud.pub_date,
        'sudoku_comments': comments
    }
    return context

def get_savedsudoku_context(sudoku_id):
    sud = get_object_or_404(SavedSudoku, pk=sudoku_id)
    return get_sudoku_context(sud)

def saved(request, sudoku_id):
    context = get_savedsudoku_context(sudoku_id)
    add_header_context(request, context)

    return render(request,'sudoku/saved.html', context)

def leave_a_comment(request, sudoku_id):
    txt = request.POST['comment']
    sud = SavedSudoku.objects.get(pk = sudoku_id)
    if len(txt) > 0:
        usr = get_logged_in_user(request)
        if usr is None:
            usr = get_anonymous_user()
        comm = SudokuComment(
            saved_sudoku = sud,
            comment_user = usr,
            comment_text = txt,
            pub_date = timezone.now()
        )
        comm.save()
    else:
        context = get_savedsudoku_context(sudoku_id)
        context['error_message'] = "Your comment is empty."
        add_header_context(request, context)
        return render(request, 'sudoku/saved.html', context)

    return HttpResponseRedirect(reverse('sudoku:saved', args=(sudoku_id,)))


def login_form(request):
    user = get_logged_in_user(request)
    if user is not None:
        return HttpResponseRedirect(reverse('sudoku:index'))

    return render(request, 'sudoku/login_form.html', {})

def login_user(request):
    user = get_logged_in_user(request)
    if user is not None:
        return HttpResponseRedirect(reverse('sudoku:index'))

    loginname = request.POST['loginname']
    password = request.POST['password']

    status = check_user_password(loginname, password)

    if not status['success']:
        return render(request, 'sudoku/login_form.html', {'error_message': status['error']})

    user = get_user_by_loginname(loginname)
    session = new_session(user)
    response = HttpResponseRedirect(reverse('sudoku:index'))
    response.set_cookie(MY_AUTH_COOKIE,session.session_id, expires = session.expires_at)
    return response

def logout_user(request):
    user = get_logged_in_user(request)
    if user is not None:
        session = get_logged_in_session(request)
        if session is not None:
            session.delete()

    response = HttpResponseRedirect(reverse('sudoku:index'))
    response.delete_cookie(MY_AUTH_COOKIE)
    return response

def register_form(request):
    user = get_logged_in_user(request)
    if user is not None:
        return HttpResponseRedirect(reverse('sudoku:index'))

    return render(request, 'sudoku/register_form.html', {})


def register_user(request):
    user = get_logged_in_user(request)
    if user is not None:
        return HttpResponseRedirect(reverse('sudoku:index'))

    loginname = request.POST['loginname']
    firstname = request.POST['firstname']
    lastname = request.POST['lastname']
    password1 = request.POST['password1']
    password2 = request.POST['password2']

    error = False
    message = ""
    if len(loginname) == 0:
        error = True
        message = message + "Login name shouldn't be empty. "

    if len(firstname) == 0:
        error = True
        message = message + "First name shouldn't be empty. "

    if len(lastname) == 0:
        error = True
        message = message + "Last name shouldn't be empty. "

    if len(password1) == 0 or len(password2) == 0:
        error = True
        message = message + "Password shouldn't be empty. "

    if password1 != password2:
        error = True
        message = message + "Passwords are different. "

    if error:
        return render(request, 'sudoku/register_form.html', {'error_message': message})

    status = create_sudoku_user(
                    loginname = loginname,
                    password = password1,
                    firstname = firstname,
                    lastname = lastname
                    )
    if not status['success']:
        return render(request, 'sudoku/register_form.html', {'error_message': status['error']})

    user = get_user_by_loginname(loginname)
    session = new_session(user)
    response = HttpResponseRedirect(reverse('sudoku:index'))
    response.set_cookie(MY_AUTH_COOKIE, session.session_id, expires=session.expires_at)
    return response