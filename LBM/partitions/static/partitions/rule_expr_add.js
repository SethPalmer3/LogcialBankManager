document.addEventListener('DOMContentLoaded', function() {
    const exprTypeSelect = document.getElementById('id_expr_type');
    const valueFields = document.getElementById('value-fields');
    const operationFields = document.getElementById('operation-fields');
    const valueInput = document.getElementById('id_value_input');
    const valueTypeSelect = document.getElementById('id_value_type');

    exprTypeSelect.addEventListener('change', function() {
        if (exprTypeSelect.value === 'value') {
            valueFields.style.display = 'block';
            operationFields.style.display = 'none';
        } else if (exprTypeSelect.value === 'operation') {
            valueFields.style.display = 'none';
            operationFields.style.display = 'block';
        } else {
            valueFields.style.display = 'none';
            operationFields.style.display = 'none';
        }
    });

    // You'll also want to handle changes in the value type to change the input type
    valueTypeSelect.addEventListener('change', function() {
        if (['float', 'decimal', 'int'].includes(valueTypeSelect.value)) {
            valueInput.type = 'number';
        } else {
            valueInput.type = 'text';
        }
    });
});
