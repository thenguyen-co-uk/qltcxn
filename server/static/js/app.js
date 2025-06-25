$(document).foundation()

function convertToDateISO8601(strDate) {
    const parts = strDate.split("/");
    const isoDate = new Date(parts[2], parts[1], parts[0]).toISOString();
    return isoDate.split('T')[0];
}