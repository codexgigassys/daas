function modifyProcessedOnInputs() {
        var inputs = [document.getElementById("id_result__processed_on_0"), document.getElementById("id_result__processed_on_1")];
        var task_status = document.getElementById("id_task__status");

        for (var element of inputs) {
            if (task_status.value != "Done" && task_status.value != "Failed") {
                element.disabled = true;
                element.value = "";
            } else {
                element.disabled = false;
            }
        }
    }

$(function(){
    modifyProcessedOnInputs()
    $("select").change(modifyProcessedOnInputs);
});