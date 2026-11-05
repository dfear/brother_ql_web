import os

from flask import current_app, render_template, request, make_response

from brother_ql.devicedependent import label_type_specs, label_sizes, two_color_support
from brother_ql.devicedependent import ENDLESS_LABEL, DIE_CUT_LABEL, ROUND_DIE_CUT_LABEL

from . import bp
from app.utils import convert_image_to_bw, convert_image_to_grayscale, pdffile_to_image, imgfile_to_image, image_to_png_bytes
from app import FONTS

from .label import SimpleLabel, LabelContent, LabelOrientation, LabelType
from .printer import PrinterQueue

LINE_SPACINGS = (100, 150, 200, 250, 300)

# Don't change as brother_ql is using this DPI value
DEFAULT_DPI = 300

LABEL_SIZES = [(
    name,
    label_type_specs[name]['name'],
    (label_type_specs[name]['kind'] in (
        ROUND_DIE_CUT_LABEL,))  # True if round label
) for name in label_sizes]


@bp.route('/')
def index():
    RED_SUPPORT = current_app.config['PRINTER_MODEL'] in two_color_support
    return render_template('labeldesigner.html',
                           font_family_names=FONTS.fontlist(),
                           label_sizes=LABEL_SIZES,
                           red_support=RED_SUPPORT,
                           default_label_size=current_app.config['LABEL_DEFAULT_SIZE'],
                           default_font_size=current_app.config['LABEL_DEFAULT_FONT_SIZE'],
                           default_orientation=current_app.config['LABEL_DEFAULT_ORIENTATION'],
                           default_font_alignment=current_app.config.get('LABEL_DEFAULT_FONT_ALIGNMENT', 'Left').lower(),
                           default_qr_size=current_app.config['LABEL_DEFAULT_QR_SIZE'],
                           default_image_mode=current_app.config['IMAGE_DEFAULT_MODE'],
                           default_bw_threshold=current_app.config['IMAGE_DEFAULT_BW_THRESHOLD'],
                           default_font_family=current_app.config['LABEL_DEFAULT_FONT_FAMILY'],
                           line_spacings=LINE_SPACINGS,
                           default_line_spacing=current_app.config['LABEL_DEFAULT_LINE_SPACING'],
                           default_dpi=DEFAULT_DPI,
                           default_margin_top=current_app.config['LABEL_DEFAULT_MARGIN_TOP'],
                           default_margin_bottom=current_app.config['LABEL_DEFAULT_MARGIN_BOTTOM'],
                           default_margin_left=current_app.config['LABEL_DEFAULT_MARGIN_LEFT'],
                           default_margin_right=current_app.config['LABEL_DEFAULT_MARGIN_RIGHT']
                           )

@bp.route('/upload')
def upload():
    RED_SUPPORT = current_app.config['PRINTER_MODEL'] in two_color_support
    return render_template('upload.html',
                           font_family_names=FONTS.fontlist(),
                           label_sizes=LABEL_SIZES,
                           red_support=RED_SUPPORT,
                           default_label_size=current_app.config['LABEL_DEFAULT_SIZE'],
                           default_font_size=current_app.config['LABEL_DEFAULT_FONT_SIZE'],
                           default_orientation=current_app.config['LABEL_DEFAULT_ORIENTATION'],
                           default_font_alignment=current_app.config.get('LABEL_DEFAULT_FONT_ALIGNMENT', 'Left').lower(),
                           default_qr_size=current_app.config['LABEL_DEFAULT_QR_SIZE'],
                           default_image_mode=current_app.config['IMAGE_DEFAULT_MODE'],
                           default_bw_threshold=current_app.config['IMAGE_DEFAULT_BW_THRESHOLD'],
                           default_font_family=current_app.config['LABEL_DEFAULT_FONT_FAMILY'],
                           line_spacings=LINE_SPACINGS,
                           default_line_spacing=current_app.config['LABEL_DEFAULT_LINE_SPACING'],
                           default_dpi=DEFAULT_DPI,
                           default_margin_top=current_app.config['LABEL_DEFAULT_MARGIN_TOP'],
                           default_margin_bottom=current_app.config['LABEL_DEFAULT_MARGIN_BOTTOM'],
                           default_margin_left=current_app.config['LABEL_DEFAULT_MARGIN_LEFT'],
                           default_margin_right=current_app.config['LABEL_DEFAULT_MARGIN_RIGHT']
                           )

@app.route('/upload/process', methods=['POST'])
def csv_upload_process_and_print():
    def render_index_with_error(error_msg):
        return render_template('index.html',
                               error=error_msg,
                               default_col=config.DEFAULT_COLUMN_NAME_LT,
                               default_col_qrcode=config.DEFAULT_COLUMN_NAME_QRT,
                               default_font=config.DEFAULT_FONT_SIZE,
                               default_copies=config.DEFAULT_COPIES,
                               default_type=config.DEFAULT_LABEL_TYPE,
                               default_workflow=config.DEFAULT_WORKFLOW,
                               gsheet_cols=config.GSHEET_DEFAULT_COLUMNS)

    if 'csv_file' not in request.files:
        return render_index_with_error("No file part uploaded.")

    file = request.files['csv_file']
    if file.filename == '':
        return render_index_with_error("No file selected.")

    workflow = request.form.get('workflow', config.DEFAULT_WORKFLOW)
    column_name_label = request.form.get('column_name_label', config.DEFAULT_COLUMN_NAME_LT)
    column_name_qrcode = request.form.get('column_name_qrtext', config.DEFAULT_COLUMN_NAME_QRT)
    font_size = request.form.get('font_size', config.DEFAULT_FONT_SIZE, type=int)
    copies = request.form.get('copies', config.DEFAULT_COPIES, type=int)
    label_type = request.form.get('label_type', config.DEFAULT_LABEL_TYPE)

    label_size = config.LABEL_DEFAULT_SIZE
    label_shape = config.LABEL_DEFAULT_SHAPE
    label_orientation = config.LABEL_DEFAULT_ORIENTATION
    label_print_colour = config.LABEL_DEFAULT_PRINT_COLOUR
    label_font_family = config.LABEL_DEFAULT_FONT_FAMILY
    label_font_style = config.LABEL_DEFAULT_FONT_STYLE
    label_font_alignment = config.LABEL_DEFAULT_FONT_ALIGNMENT
    label_line_spacing = config.LABEL_DEFAULT_LINE_SPACING
    label_qr_size = config.LABEL_DEFAULT_QR_SIZE
    label_margin_top = config.LABEL_DEFAULT_MARGIN_TOP
    label_margin_bottom = config.LABEL_DEFAULT_MARGIN_BOTTOM
    label_margin_left = config.LABEL_DEFAULT_MARGIN_LEFT
    label_margin_right = config.LABEL_DEFAULT_MARGIN_RIGHT

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)

    success_count = 0
    fail_count = 0

    if workflow == 'process_master':
        csv_reader = csv.reader(stream)
        filter_ids = [str(row[0]).strip() for row in csv_reader if row]

        if not filter_ids:
            return render_index_with_error("Uploaded CSV is empty.")

        try:
            inventory_data = get_inventory_data()
        except Exception as e:
            return render_index_with_error(f"Error communicating with Google Sheets API: {str(e)}")

        filtered_df = process_label_data(inventory_data, filter_ids)

        if filtered_df.empty:
            return render_index_with_error("No matching inventory IDs were found in the Google Sheet.")

        for index, row in filtered_df.iterrows():
            label_text = row.get(column_name_label)
            qr_text = row.get(column_name_qrcode)

            if debug_mode:
                 print(f"Processing row {index}: label_text='{label_text}', qr_text='{qr_text}'")  # Debugging output
                 sys.exit(0)  # Stop after first row for debugging

            if pd.notna(label_text) and str(label_text).strip() != "":
                if send_to_printer(str(label_text), str(qr_text), font_size, copies, label_type, label_size, label_shape, label_orientation, label_print_colour, label_font_family, label_font_style, label_font_alignment, label_line_spacing, label_qr_size, label_margin_top, label_margin_bottom, label_margin_left, label_margin_right):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1

    elif workflow == 'direct_print':
        csv_reader = csv.DictReader(stream)

        if not csv_reader.fieldnames or column_name_label not in csv_reader.fieldnames or column_name_qrcode not in csv_reader.fieldnames:
             return render_index_with_error(f"Column '{column_name_label}' or '{column_name_qrcode}' not found in the uploaded CSV. Available columns: {', '.join(csv_reader.fieldnames or ['None'])}")

        for row in csv_reader:
            label_text = row.get(column_name_label)
            qr_text = row.get(column_name_qrcode)

            #print(f"Processing row: label_text='{label_text}', qr_text='{qr_text}'")  # Debugging output
            #sys.exit(0)  # Stop after first row for debugging

            if label_text or qr_text and str(label_text).strip() != "" or str(qr_text).strip() != "":
                if send_to_printer(str(label_text), str(qr_text), font_size, copies, label_type, label_size, label_shape, label_orientation, label_print_colour, label_font_family, label_font_style, label_font_alignment, label_line_spacing, label_qr_size, label_margin_top, label_margin_bottom, label_margin_left, label_margin_right):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1

    return render_template('result.html', success_count=success_count, fail_count=fail_count)

@bp.route('/api/font/styles', methods=['POST', 'GET'])
def get_font_styles():
    font = request.values.get(
        'font', current_app.config['LABEL_DEFAULT_FONT_FAMILY'])
    return FONTS.fonts[font]


@bp.route('/api/preview', methods=['POST', 'GET'])
def get_preview_from_image():
    label = create_label_from_request(request)
    im = label.generate()

    return_format = request.values.get('return_format', 'png')

    if return_format == 'base64':
        import base64
        response = make_response(base64.b64encode(image_to_png_bytes(im)))
        response.headers.set('Content-type', 'text/plain')
        return response
    else:
        response = make_response(image_to_png_bytes(im))
        response.headers.set('Content-type', 'image/png')
        return response


@bp.route('/api/print', methods=['POST', 'GET'])
def print_text():
    """
    API to print a label

    returns: JSON

    Ideas for additional URL parameters:
    - alignment
    """

    return_dict = {'success': False}

    try:
        printer = create_printer_from_request(request)
        label = create_label_from_request(request)
        print_count = int(request.values.get('print_count', 1))
        cut_once = int(request.values.get('cut_once', 0)) == 1
    except Exception as e:
        return_dict['message'] = str(e)
        current_app.logger.error('Exception happened: %s', e)
        return return_dict

    printer.add_label_to_queue(label, print_count, cut_once)

    try:
        printer.process_queue()
    except Exception as e:
        return_dict['message'] = str(e)
        current_app.logger.error('Exception happened: %s', e)
        return return_dict

    return_dict['success'] = True
    return return_dict


def create_printer_from_request(request):
    d = request.values
    context = {
        'label_size': d.get('label_size', '62')
    }

    return PrinterQueue(
        model = current_app.config['PRINTER_MODEL'],
        device_specifier = current_app.config['PRINTER_PRINTER'],
        label_size = context['label_size']
    )


def create_label_from_request(request):
    d=request.values
    context={
        'label_size': d.get('label_size', '62'),
        'print_type': d.get('print_type', 'text'),
        'label_orientation': d.get('orientation', 'standard'),
        'kind': label_type_specs[d.get('label_size', "62")]['kind'],
        'margin_top': float(d.get('margin_top', 24))/100.,
        'margin_bottom': float(d.get('margin_bottom', 45))/100.,
        'margin_left': float(d.get('margin_left', 35))/100.,
        'margin_right': float(d.get('margin_right', 35))/100.,
        'qrtext': d.get('qrtext', None),
        'text': d.get('text', None),
        'align': d.get('align', 'center'),
        'qrcode_size': int(d.get('qrcode_size', 10)),
        'qrcode_correction': d.get('qrcode_correction', 'L'),
        'image_mode': d.get('image_mode', "grayscale"),
        'image_bw_threshold': int(d.get('image_bw_threshold', 70)),
        'font_size': int(d.get('font_size', 100)),
        'line_spacing': int(d.get('line_spacing', 100)),
        'font_family': d.get('font_family'),
        'font_style': d.get('font_style'),
        'print_color': d.get('print_color', 'black'),
    }

    def get_label_dimensions(label_size):
        try:
            ls = label_type_specs[context['label_size']]
        except KeyError:
            raise LookupError("Unknown label_size")
        return ls['dots_printable']

    def get_font_path(font_family_name, font_style_name):
        # Fallback if font_family_name is missing, empty, or invalid
        if not font_family_name or not FONTS.fonts.get(font_family_name):
            font_family_name = current_app.config.get('LABEL_DEFAULT_FONT_FAMILY')

            # If the default is still missing or invalid, grab the first valid font
            if not font_family_name or not FONTS.fonts.get(font_family_name):
                valid_fonts = [f for f, styles in FONTS.fonts.items() if styles]
                if valid_fonts:
                    font_family_name = valid_fonts[0]
                else:
                    raise LookupError("No fonts available")

        # Fallback if font_style_name is missing or invalid for the selected family
        available_styles = list(FONTS.fonts.get(font_family_name, {}).keys())
        if not font_style_name or font_style_name not in available_styles:
            if available_styles:
                font_style_name = 'Regular' if 'Regular' in available_styles else available_styles[0]
            else:
                raise LookupError("No styles available for font")

        try:
            font_path = FONTS.fonts[font_family_name][font_style_name]
            return font_path
        except KeyError:
            raise LookupError("Couldn't find the font & style")

    def get_uploaded_image(image):
        try:
            name, ext = os.path.splitext(image.filename)
            if ext.lower() in ('.png', '.jpg', '.jpeg'):
                image = imgfile_to_image(image)
                if context['image_mode'] == 'grayscale':
                    return convert_image_to_grayscale(image)
                else:
                    return convert_image_to_bw(image, context['image_bw_threshold'])
            elif ext.lower() in ('.pdf'):
                image = pdffile_to_image(image, DEFAULT_DPI)
                if context['image_mode'] == 'grayscale':
                    return convert_image_to_grayscale(image)
                else:
                    return convert_image_to_bw(image, context['image_bw_threshold'])
            else:
                return None
        except AttributeError:
            return None

    if context['print_type'] == 'text':
        label_content = LabelContent.TEXT_ONLY
    elif context['print_type'] == 'qrcode':
        label_content = LabelContent.QRCODE_ONLY
    elif context['print_type'] == 'qrcode_text':
        label_content = LabelContent.TEXT_QRCODE
    elif context['image_mode'] == 'grayscale':
        label_content = LabelContent.IMAGE_GRAYSCALE
    else:
        label_content = LabelContent.IMAGE_BW

    if context['label_orientation'] == 'rotated':
        label_orientation = LabelOrientation.ROTATED
    else:
        label_orientation = LabelOrientation.STANDARD

    if context['kind'] == ENDLESS_LABEL:
        label_type = LabelType.ENDLESS_LABEL
    elif context['kind'] == DIE_CUT_LABEL:
        label_type = LabelType.DIE_CUT_LABEL
    else:
        label_type = LabelType.ROUND_DIE_CUT_LABEL

    width, height = get_label_dimensions(context['label_size'])
    if height > width:
        width, height = height, width
    if label_orientation == LabelOrientation.ROTATED:
        height, width = width, height

    return SimpleLabel(
        width=width,
        height=height,
        label_content=label_content,
        label_orientation=label_orientation,
        label_type=label_type,
        label_margin=(
            int(context['font_size']*context['margin_left']),
            int(context['font_size']*context['margin_right']),
            int(context['font_size']*context['margin_top']),
            int(context['font_size']*context['margin_bottom'])
        ),
        fore_color=
            (255, 0, 0) if 'red' in context['label_size'] and context['print_color'] == 'red'
            else (0, 0, 0),
        qrtext=context['qrtext'],
        text=context['text'],
        text_align=context['align'],
        qr_size=context['qrcode_size'],
        qr_correction=context['qrcode_correction'],
        image=get_uploaded_image(request.files.get('image', None)),
        font_path=get_font_path(context['font_family'], context['font_style']),
        font_size=context['font_size'],
        line_spacing=context['line_spacing']
    )
