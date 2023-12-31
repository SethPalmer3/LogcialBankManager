document.addEventListener('DOMContentLoaded', function() {
    const exprTypeSelect = document.getElementById('id_expr_type');
    const valueFields = document.getElementById('value-fields');
    const operationFields = document.getElementById('operation-fields');
    const refFields = document.getElementById('ref-fields');
    const refAttrFields = document.getElementById('ref-attr-fields');
    const valueInput = document.getElementById('id_value_input');
    const valueTypeSelect = document.getElementById('id_value_type');
    // const refTypeSelect = document.getElementById('id_ref_type');
    const refSelect = document.getElementById('id_ref_ents');
    const refAttrSelect = document.getElementById('id_ref_attrs');

    function updateFormFields() {
        if (exprTypeSelect.value === 'value') {
            valueFields.style.display = 'block';
            refFields.style.display = 'none';
            refAttrFields.style.display = 'none';
            operationFields.style.display = 'none';
        } else if (exprTypeSelect.value === 'operation') {
            valueFields.style.display = 'none';
            refFields.style.display = 'none';
            refAttrFields.style.display = 'none';
            operationFields.style.display = 'block';
        } else if (exprTypeSelect.value === 'reference') {
            valueFields.style.display = 'none';
            refFields.style.display = 'block';
            refAttrFields.style.display = 'block';
            operationFields.style.display = 'none';
            select_values = refSelect.value.split(',');
            for (let i=0; i<refAttrSelect.children.length; i++){
                attr_type = refAttrSelect.children[i].value.split(',')[0];
                console.log(attr_type);
                if (attr_type === select_values[1]){
                    refAttrSelect.children[i].style.display = 'block';
                }else{
                    refAttrSelect.children[i].style.display = 'none';
                }
            }
        } else {
            valueFields.style.display = 'none';
            operationFields.style.display = 'none';
            refFields.style.display = 'none';
            refAttrFields.style.display = 'none';
        }
        updateValueInput();
    }

    function updateValueInput() {
        if (['float', 'decimal', 'int'].includes(valueTypeSelect.value)) {
            valueInput.type = 'number';
        } else {
            valueInput.type = 'text';
        }
    }

    // Attach the event listeners
    exprTypeSelect.addEventListener('change', updateFormFields);
    refSelect.addEventListener('change', updateFormFields);
    valueTypeSelect.addEventListener('change', updateValueInput);

    // Initialize the form fields on page load
    updateFormFields();
});
