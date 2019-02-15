function modifyProcessedOnInputs() {
        var inputs = [document.getElementById("id_result__processed_on_0"), document.getElementById("id_result__processed_on_1")];
        var redis_job_status = document.getElementById("id_redisjob__status");

        for (var element of inputs) {
            if (redis_job_status.value != "Done" && redis_job_status.value != "Failed") {
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