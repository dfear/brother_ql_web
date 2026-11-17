// Store the default variables passed from Python
const defaultColumnNameLT = "{{ default_col }}";
const defaultColumnNameQRT = "{{ default_col_qrcode }}";

// Parse the Python list into a JavaScript array using Jinja's 'tojson' filter
const gsheetColumns = {{ gsheet_cols | tojson | safe }};

document.getElementById('btnProcessCsv').addEventListener('click', function () {
  const fileInput = document.getElementById('csvFile');
  const step2Div = document.getElementById('step2');
  const currentWorkflow = document.getElementById('workflow').value;

  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Error: Please select a CSV file to upload before processing.");
    return;
  }

  const file = fileInput.files[0];
  const reader = new FileReader();

  reader.onload = function (event) {
    const text = event.target.result;
    const firstLine = text.split('\n')[0];

    let columns = firstLine.split(',').map(col => col.replace(/['"\r]+/g, '').trim());

    const selectElementQRText = document.getElementById('columnNameQRText');
    selectElementQRText.innerHTML = '';

    const selectElementLabelText = document.getElementById('columnNameLabelText');
    selectElementLabelText.innerHTML = '';

    // 1. Always inject the raw CSV columns
    columns.forEach(col => {
      if (col) {
        let option = document.createElement('option');
        option.value = col;
        option.text = col + " (from CSV)";
        selectElementQRText.appendChild(option);
      }
    });

    columns.forEach(col => {
      if (col) {
        let option = document.createElement('option');
        option.value = col;
        option.text = col + " (from CSV)";
        selectElementLabelText.appendChild(option);
      }
    });


    // 2. Only inject Google Sheet defaults if Option 1 is selected
    if (currentWorkflow === 'process_master') {
      gsheetColumns.forEach(col => {
        // Prevent adding a duplicate if the CSV happens to contain a column like "inventory_id"
        let existingOption = Array.from(selectElementQRText.options).find(opt => opt.value === col);

        if (!existingOption) {
          let option = document.createElement('option');
          option.value = col;
          option.text = col + " (Default/Google Sheet)";
          selectElementQRText.appendChild(option);
        }

        // Prevent adding a duplicate if the CSV happens to contain a column like "inventory_id"
        let existingOption2 = Array.from(selectElementLabelText.options).find(opt => opt.value === col);

        if (!existingOption2) {
          let option = document.createElement('option');
          option.value = col;
          option.text = col + " (Default/Google Sheet)";
          selectElementLabelText.appendChild(option);
        }
      });


    }

    // 3. Try to auto-select the main default from config.py if it exists in the list
    let defaultExistsQRT = Array.from(selectElementQRText.options).some(opt => opt.value === defaultColumnNameQRT);
    if (defaultExistsQRT) {
      selectElementQRText.value = defaultColumnNameQRT;
    } else if (selectElementQRText.options.length > 0) {
      // Fallback to the first available option
      selectElementQRText.selectedIndex = 0;
    }

    let defaultExistsLT = Array.from(selectElementLabelText.options).some(opt => opt.value === defaultColumnNameLT);
    if (defaultExistsLT) {
      selectElementLabelText.value = defaultColumnNameLT;
    } else if (selectElementLabelText.options.length > 0) {
      // Fallback to the first available option
      selectElementLabelText.selectedIndex = 0;
    }

    step2Div.style.display = 'block';
  };

  reader.readAsText(file);
});

// Hide Step 2 if the user changes the file or changes the workflow midway
document.getElementById('csvFile').addEventListener('change', function () {
  document.getElementById('step2').style.display = 'none';
});

document.getElementById('workflow').addEventListener('change', function () {
  document.getElementById('step2').style.display = 'none';
});