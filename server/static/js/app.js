$(document).foundation();

function convertToDateISO8601(strDate) {
    const parts = strDate.split("/");
    // because the view shows and the datetime picker is set dd/mm/yyyy
    // JavaScript counts months from 0 to 11;
    // hours=2 makes sure that the system instantiates the exact date
    // chosen from the datetime picker regardless of BST
    let isoDate = new Date(parts[2], parts[1]-1, parts[0],2,0,0);
    isoDate = isoDate.toISOString();
    console.log(isoDate);
    return isoDate.split('T')[0];
}

function convertToISODateTime() {
    const d = new Date(); // for now
    const hour = d.getHours() < 10 ? "0" + d.getHours().toString() : d.getHours();
    const minute = d.getMinutes() < 10 ? "0" + d.getMinutes().toString() : d.getMinutes();
    const second = d.getSeconds() < 10 ? "0" + d.getSeconds().toString() : d.getSeconds();
    return " " + hour + ":" + minute + ":"+ second;
}

function getTimestamp(strDate) {
    const date = new Date(strDate);
    return date.getTime()/1000;
}

function calStartAndEndDayOfWeek(givenDate = null) {
    let curr = new Date; // get current date
    if (givenDate) {
        // ex: "1970-01-01T00:00:00Z" or "1970-01-01"
        curr = new Date(givenDate);
    }
    // First day is the day of the month - the day of the week
    const first = curr.getDate() - curr.getDay() + (curr.getDay() === 0 ? -6 : 1);
    const last = first + 6; // last day is the first day + 6

    const firstDay = new Date(curr.setDate(first)).toUTCString();
    const lastDay = new Date(curr.setDate(last)).toUTCString();
    console.log(firstDay, lastDay);
    return [firstDay, lastDay]
}

function startOfWeek(date) {
    const diff = date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1);
    return new Date(date.setDate(diff));
}