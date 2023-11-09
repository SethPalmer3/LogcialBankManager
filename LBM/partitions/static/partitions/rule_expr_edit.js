document.addEventListener('DOMContentLoaded', function() {
    const valueTypeSelect = document.getElementById('id_value_or_ref');
    const fixedValues = document.getElementById('fix_values');
    const fixedValueType = document.getElementById('id_value_type');
    const fixedValueInput = document.getElementById('id_value_input');
    const refValues = document.getElementById('ref_values');
    const refSelect = document.getElementById('id_ref_ents');
    const refAttrSelect = document.getElementById('id_ref_attrs');

    function updateFormFields(){
        if (valueTypeSelect.value === 'value'){
            fixedValues.style.display = "block";
            refValues.style.display = "none";
        }else if(valueTypeSelect.value === 'reference'){
            select_values = refSelect.value.split(',');
            console.log(select_values);
            for (let i=0; i<refAttrSelect.children.length; i++){
                attr_type = refAttrSelect.children[i].value.split(',')[0];
                console.log(attr_type);
                if (attr_type === select_values[1]){
                    refAttrSelect.children[i].style.display = 'block';
                }else{
                    refAttrSelect.children[i].style.display = 'none';
                }
            }
            fixedValues.style.display = "none";
            refValues.style.display = "block";
        }else{
            fixedValues.style.display = "none";
            refValues.style.display = "none";
        }
        updateValueInput();
    }

    function updateValueInput() {
        if (['float', 'decimal', 'int'].includes(fixedValueType.value)) {
            fixedValueInput.type = 'number';
        } else {
            fixedValueInput.type = 'text';
        }
        
    }
    valueTypeSelect.addEventListener('change', updateFormFields);
    fixedValueType.addEventListener('change', updateFormFields);
    refValues.addEventListener('change', updateFormFields);
    updateFormFields();
    
})
