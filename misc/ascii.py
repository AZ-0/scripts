'''https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797'''

# General ASCII Codes

BELL      = BEL = '\x07' # Terminal bell
BACKSPACE = BS  = '\x08' # Backspace
HORI_TAB  = HT  = '\x09' # Horizontal TAB
LINEFEED  = LF  = '\x0A' # Linefeed
NEWLINE   = NL  = LF     # New line
VERT_TAB  = VT  = '\x0B' # Vertical TAB
FORMFEED  = FF  = '\x0C' # Formeed
NEWPAGE   = NP  = FF     # New page
CARRIAGE  = CR  = '\x0D' # Carriage return
ESCAPE    = ESC = '\x1B' # Escape character
DELETE    = DEL = '\x7F' # Delete character


# Cursor Controls

CURSOR_QUERY   = CurQ   = '\x1B[6n'  # Requests cursor position (reports as ESC[#;#R)
CURSOR_HOME    = CurH   = '\x1B[H'   # Moves cursor to home position (0, 0)
CURSOR_MOVE_XY = CurMXY = lambda x,y: f'\x1B[{y};{x}H' # Moves cursor to line #, column #
CURSOR_MOVE_X  = CurMX  = lambda x:   f'\x1B[{x}G'     # Moves cursor to column #

CURSOR_UP      = CurU  = '\x1B[A' # Moves cursor up 1 line
CURSOR_DOWN    = CurD  = '\x1B[B' # Moves cursor down 1 line
CURSOR_RIGHT   = CurR  = '\x1B[C' # Moves cursor right 1 line
CURSOR_LEFT    = CurL  = '\x1B[D' # Moves cursor left 1 line
CURSOR_DOWN_NL = CurDL = '\x1B[E' # Moves cursor to beginning of next line, 1 line down
CURSOR_UP_NL   = CurUL = '\x1B[F' # Moves cursor to beginning of prev line, 1 line up

CURSOR_UP_N      = CurUN  = lambda n: f'\x1B[{n}A' # Moves cursor up n lines
CURSOR_DOWN_N    = CurDN  = lambda n: f'\x1B[{n}B' # Moves cursor down n lines
CURSOR_RIGHT_N   = CurLN  = lambda n: f'\x1B[{n}C' # Moves cursor right n lines
CURSOR_LEFT_N    = CurRN  = lambda n: f'\x1B[{n}D' # Moves cursor left n lines
CURSOR_DOWN_NL_N = CurDLN = lambda n: f'\x1B[{n}E' # Moves cursor to beginning of next line, n lines down
CURSOR_UP_NL_N   = CurULN = lambda n: f'\x1B[{n}F' # Moves cursor to beginning of prev line, n lines up

CURSOR_UP_SCROLL   = CurUS     = '\x1B M' # Moves cursor one line up, scrolling if needed
CURSOR_SAVE_XY     = CurSXY    = '\x1B 7' # Saves cursor position (DEC)
CURSOR_LOAD_XY     = CurLXY    = '\x1B 8' # Restores the cursor to the last saved position (DEC)
CURSOR_SAVE_XY_SCO = CurSXYSCO = '\x1B[s' # Saves cursor position (SCO)
CURSOR_LOAD_XY_SCO = CurLXYSCO = '\x1B[s' # Restores the cursor to the last saved position (SCO)


# Erase Functions

ERASE_IN_DISPLAY         = EraDisp = '\x1B[J'  # Erases in display (same as ESC[0J)
ERASE_SCREEN_FROM_CURSOR = EraScFC = '\x1B[0J' # Erases from cursor until end of screen
ERASE_SCREEN_TILL_CURSOR = EraScTC = '\x1B[1J' # Erases from cursor to beginning of screen
ERASE_LINE_FROM_CURSOR   = EraLnFC = '\x1B[0K' # Erases from cursor to end of line
ERASE_LINE_TILL_CURSOR   = EraLnTC = '\x1B[1K' # Erases start of line to the cursor
ERASE_SCREEN  = EraSc  = '\x1B[2J'             # Erases entire screen
ERASE_LINE    = EraLn  = '\x1B[2K'             # Erases the entire line
ERASE_IN_LINE = EraILn = '\x1B[K'              # Erases in line (same as ESC[0K)
ERASE_SAVED   = EraSv  = '\x1B[3J'             # Erases saved lines


# Graphics Mode

RESET     = Rst = '\x1B[0m'
BOLD      = Bld = '\x1B[1m'
DIM       = Dim = '\x1B[2m'
ITALIC    = Ita = '\x1B[3m'
UNDERLINE = Udl = '\x1B[4m'
BLINK     = Bli = '\x1B[5m'
REVERSE   = Rev = '\x1B[7m'
HIDDEN    = Hid = '\x1B[8m'
STRIKED   = Stk = '\x1B[9m'

RESET_BOLD      = RstBld = '\x1B[22m'
RESET_DIM       = RstDim = RESET_BOLD
RESET_ITALIC    = RstIta = '\x1B[23m'
RESET_UNDERLINE = RstUdl = '\x1B[24m'
RESET_BLINK     = RstBli = '\x1B[25m'
RESET_REVERSE   = RstRev = '\x1B[27m'
RESET_HIDDEN    = RstHid = '\x1B[28m'
RESET_STRIKED   = RstStk = '\x1B[29m'

FG_BLACK     = FgBlk  = '\x1B[30m'
FG_RED       = FgRed  = '\x1B[31m'
FG_GREEN     = FgGrn  = '\x1B[32m'
FG_YELLOW    = FgYlw  = '\x1B[33m'
FG_BLUE      = FgBlu  = '\x1B[34m'
FG_MAGENTA   = FgMgt  = '\x1B[35m'
FG_CYAN      = FgCya  = '\x1B[36m'
FG_WHITE     = FgWhi  = '\x1B[37m'
FG_DEFAULT   = FgDflt = '\x1B[39m'

BG_BLACK     = BgBlk  = '\x1B[40m'
BG_RED       = BgRed  = '\x1B[41m'
BG_GREEN     = BgGrn  = '\x1B[42m'
BG_YELLOW    = BgYlw  = '\x1B[43m'
BG_BLUE      = BgBlu  = '\x1B[44m'
BG_MAGENTA   = BgMgt  = '\x1B[45m'
BG_CYAN      = BgCya  = '\x1B[46m'
BG_WHITE     = BgWhi  = '\x1B[47m'
BG_DEFAULT   = BgDflt = '\x1B[49m'

FG_B_BLACK   = BgBBlk = '\x1B[90m'
FG_B_RED     = BgBRed = '\x1B[91m'
FG_B_GREEN   = BgBGrn = '\x1B[92m'
FG_B_YELLOW  = BgBYlw = '\x1B[93m'
FG_B_BLUE    = BgBBlu = '\x1B[94m'
FG_B_MAGENTA = BgBMgt = '\x1B[95m'
FG_B_CYAN    = BgBCya = '\x1B[96m'
FG_B_WHITE   = BgBWhi = '\x1B[97m'

BG_B_BLACK   = BgBBlk = '\x1B[100m'
BG_B_RED     = BgBRed = '\x1B[101m'
BG_B_GREEN   = BgBGrn = '\x1B[102m'
BG_B_YELLOW  = BgBYlw = '\x1B[103m'
BG_B_BLUE    = BgBBlu = '\x1B[104m'
BG_B_MAGENTA = BgBMgt = '\x1B[105m'
BG_B_CYAN    = BgBCya = '\x1B[106m'
BG_B_WHITE   = BgBWhi = '\x1B[107m'

SET_FG_COLOR_ID  = lambda id: f'\x1B[38;5;{id}m'
SET_BG_COLOR_ID  = lambda id: f'\x1B[48;5;{id}m'
SET_FG_COLOR_RGB = lambda r,g,b: f'\x1B[38;2;{r};{g};{b}m'
SET_BG_COLOR_RGB = lambda r,g,b: f'\x1B[48;2;{r};{g};{b}m'


# Screen Modes