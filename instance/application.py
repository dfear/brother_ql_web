""" User specific application settings """
import logging
PRINTER_MODEL = 'QL-500'
""" PRINTER_PRINTER = 'usb://0x04f9:0x2015' """
PRINTER_PRINTER = 'tcp://127.0.0.1:9100'

""" PRINTER_PRINTER = 'file:///dev/usb/lp1' """
""" file:///dev/lp/printers/usb-Brother_QL-500_F4Z731433 """

""" LABEL_DEFAULT_SIZE = '23x23'
LABEL_DEFAULT_SHAPE = 'SQUARE'
LABEL_DEFAULT_ORIENTATION = 'rotated'
LABEL_DEFAULT_PRINT_COLOUR = 'Black'
LABEL_DEFAULT_FONT_FAMILY = 'Liberation Mono'
LABEL_DEFAULT_FONT_STYLE = 'Regular'
LABEL_DEFAULT_FONT_SIZE = 37
LABEL_DEFAULT_FONT_ALIGNMENT = 'Centre'
LABEL_DEFAULT_LINE_SPACING = 100
LABEL_DEFAULT_QR_SIZE = 6
#LABEL_DEFAULT_ERROR_CORRECTION = 'L'
LABEL_DEFAULT_MARGIN_TOP = 20
LABEL_DEFAULT_MARGIN_BOTTOM = 20
LABEL_DEFAULT_MARGIN_LEFT = 20
LABEL_DEFAULT_MARGIN_RIGHT = 20

#IMAGE_DEFAULT_MODE = ''
#IMAGE_DEFAULT_BW_THRESHOLD = ''  """

LABEL_DEFAULT_SIZE = '17x54'
LABEL_DEFAULT_SHAPE = 'RECT'
LABEL_DEFAULT_ORIENTATION = 'standard'
LABEL_DEFAULT_PRINT_COLOUR = 'Black'
LABEL_DEFAULT_FONT_FAMILY = 'FreeMono'
LABEL_DEFAULT_FONT_STYLE = 'Regular'
LABEL_DEFAULT_FONT_SIZE = 50
LABEL_DEFAULT_FONT_ALIGNMENT = 'Left'
LABEL_DEFAULT_LINE_SPACING = 100
LABEL_DEFAULT_QR_SIZE = 6
#LABEL_DEFAULT_ERROR_CORRECTION = 'L'
LABEL_DEFAULT_MARGIN_TOP = 20
LABEL_DEFAULT_MARGIN_BOTTOM = 20
LABEL_DEFAULT_MARGIN_LEFT = 20
LABEL_DEFAULT_MARGIN_RIGHT = 20

#IMAGE_DEFAULT_MODE = ''
#IMAGE_DEFAULT_BW_THRESHOLD = ''

# ==========================================
# Google Sheets & Printer Configuration
# ==========================================
GSPREAD_JSON_KEY = '/home/dfear/Pickle IT/projects/software/python_gspread/barcode-scanner-master-data/pygsheetstest-382821-9f6534beb8f8.json'
#GSPREAD_JSON_KEY = '/home/lpr/api_keys/python_gspread/pygsheetstest-382821-9f6534beb8f8.json'
SPREADSHEET_ID = '1oA2Cnd8MMToabdR3TJZJHx299DMDUZPt5-2LBMPDejQ'
SHEET_NAME = 'inventory'
# Default columns to inject ONLY when using the Google Sheets workflow (Option 1)
GSHEET_DEFAULT_COLUMNS = ['label_text', 'inventory_id', 'specifications']

#PRINTER_URL = "http://printerpi.lan:5000/labeldesigner/api/print"

# ==========================================
# Default Print Settings (Step 2)
# ==========================================
CSV_UPLOAD_DEFAULT_WORKFLOW = 'direct_print'  # Sets Option 2 as the default
CSV_UPLOAD_DEFAULT_COLUMN_NAME_LT = 'label_text'
CSV_UPLOAD_DEFAULT_COLUMN_NAME_QRT = 'inventory_id'
CSV_UPLOAD_DEFAULT_FONT_SIZE = 48 # Default font size for labels
CSV_UPLOAD_DEFAULT_COPIES = 1
CSV_UPLOAD_DEFAULT_LABEL_TYPE = 'qrcode_text' # default for inventory labels