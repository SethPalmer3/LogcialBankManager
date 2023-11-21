var transfer_to_value;
var transfer_from_value;
var action_select_value;
var transfer_amount;
document.addEventListener('DOMContentLoaded', function() {
    const ActionSelect = document.getElementById('id_action');
    action_select_value = ActionSelect.value
    const ActionTransferFrom = document.getElementById('id_transfer_from');
    transfer_from_value = ActionTransferFrom.value
    const ActionTransferTo = document.getElementById('id_transfer_to');
    transfer_to_value = ActionTransferTo.value
    const ActionForm = document.getElementById('action_form');
    const ActionTransferAmount = document.getElementById('id_transfer_amount')
    transfer_amount = ActionTransferAmount.value

    function updateFormFields(){
        if (ActionSelect.value === 'transfer'){
            ActionTransferFrom.style.display = 'block';
            ActionTransferTo.style.display = 'block';
            ActionTransferAmount.style.display = 'block';
        }else{
            ActionTransferFrom.style.display = 'none';
            ActionTransferTo.style.display = 'none';
            ActionTransferAmount.style.display = 'none';
        }
        if (ActionTransferFrom.value !== transfer_from_value ||
            ActionTransferTo.value !== transfer_to_value ||
            ActionSelect.value !== action_select_value ||
            ActionTransferAmount.value !== transfer_amount){
            transfer_from_value = ActionTransferFrom.value
            transfer_to_value = ActionTransferTo.value
            action_select_value = ActionSelect.value
            ActionForm.submit();
        }
    }

    ActionSelect.addEventListener('change', updateFormFields);
    ActionTransferFrom.addEventListener('change', updateFormFields);
    ActionTransferTo.addEventListener('change', updateFormFields);
    ActionTransferAmount.addEventListener('focusout', updateFormFields);
    // window.onbeforeunload = updateFormFields();
    updateFormFields();
})
