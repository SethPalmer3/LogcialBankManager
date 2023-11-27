var transfer_to_value;
var action_select_value;
var transfer_amount;
document.addEventListener('DOMContentLoaded', function() {
    const ActionSelect = document.getElementById('id_action');
    action_select_value = ActionSelect.value
    const ActionTransferTo = document.getElementById('id_transfer_to');
    transfer_to_value = ActionTransferTo.value
    const ActionForm = document.getElementById('action_form');
    const ActionTransferAmount = document.getElementById('id_transfer_amount')
    transfer_amount = ActionTransferAmount.value

    function updateFormFields(){
        if (ActionSelect.value === 'transfer'){
            ActionTransferTo.style.display = 'block';
            ActionTransferAmount.style.display = 'block';
        }else{
            ActionTransferTo.style.display = 'none';
            ActionTransferAmount.style.display = 'none';
        }
        if (ActionTransferTo.value !== transfer_to_value ||
            ActionSelect.value !== action_select_value ||
            ActionTransferAmount.value !== transfer_amount){
            transfer_to_value = ActionTransferTo.value
            action_select_value = ActionSelect.value
            ActionForm.submit();
        }
    }

    ActionSelect.addEventListener('change', updateFormFields);
    ActionTransferTo.addEventListener('change', updateFormFields);
    ActionTransferAmount.addEventListener('focusout', updateFormFields);
    // window.onbeforeunload = updateFormFields();
    updateFormFields();
})
