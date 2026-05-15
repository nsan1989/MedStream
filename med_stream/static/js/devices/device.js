document.addEventListener("DOMContentLoaded", function() {

    const facility = document.getElementById("id_facility");
    const block = document.getElementById("id_block");
    const floor = document.getElementById("id_floor");

    if (!facility) return;

    facility.addEventListener("change", function() {

        const facilityId = this.value;

        block.innerHTML = `<option value="">Select Block</option>`
        floor.innerHTML = `<option value="">Select Floor</option>`

        if (!facilityId) return;

        fetch(`/device/settings/ajax/load_blocks/?facility_id=${facilityId}`).then(
            response => response.json()
        ).then(data=> {
            data.forEach(
                item => {
                    const option = document.createElement("option");
                    option.value = item.id;
                    option.textContent = item.name;
                    block.appendChild(option);
                }
            );
        })
        .catch(error => {
            console.error(
                "Error loading blocks:",
                error
            );
        });
    });

    block.addEventListener("change", function() {

        const blockId = this.value;

        floor.innerHTML = `<option value="">Select Floor</option>`

        if (!blockId) return;

        fetch(`/device/settings/ajax/load_floors/?block_id=${blockId}`).then(
            response => response.json()
        ).then(data=> {
            data.forEach(
                item => {
                    const option = document.createElement("option");
                    option.value = item.id;
                    option.textContent = item.name;
                    floor.appendChild(option);
                }
            );
        })
        .catch(error => {
            console.error(
                "Error loading floors:",
                error
            );
        });
    });

});