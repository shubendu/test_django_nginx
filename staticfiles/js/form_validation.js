function getValuesByClassName(name) {
    const elements = document.getElementsByClassName(name);
    const values = [];
    for (let i = 0; i < elements.length; i++) {
        values.push(elements[i].value);
    }
    return values;
}
function removeEmptyValues(arr) {
    return arr.filter((value) => value !== undefined && value !== null && value.trim() !== '');
  }
function validateForm() {
    let errorMessage = "";
    let sortOrderValues = getValuesByClassName('sort_order');
    sortOrderValues = removeEmptyValues(sortOrderValues);

    // check length
    if (sortOrderValues.length === 0) {
        return true;
    }
    sortOrderValues.sort((a, b) => a - b);

    const allZeros = sortOrderValues.every(element => element === "0");
    if (allZeros) {
        return true;
    }else{
        // check sort order contains 1
        // if (sortOrderValues[0] !=1) {
        //     errorMessage = "Sort order should include number 1";
        //     alert(errorMessage);
        //     return false;
        // }
    }
    
    // check if any number missing between first and last sort order
    // let checkSequence = sortOrderValues[sortOrderValues.length - 1] == sortOrderValues.length;
    // if (!checkSequence) {
    //     errorMessage = "Some issue with sort orders, please check.";
    //     errorMessage += "\n\nYour Inputs:"+sortOrderValues;
    //     alert(errorMessage);
    //     return false;
    // }
    return true;
}