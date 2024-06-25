// table export
function init_excel_export(selector, filename) {
    // block the other tabs
    // It is checked for working with firefox and chrome.
    if (document.body.clientHeight <= 0) return;

    let now = new Date();
    let month = now.getMonth()+1; if(month.toString().length < 2) { month = '0' + month }
    let day = now.getDate(); if(day.toString().length < 2) { day = '0' + month }
    let date = now.getFullYear() + '_' + month + '_' + day;

    let rfn = filename + '-' + date;
    console.log(rfn);
    selector.tableExport({fileName: rfn, type:'excel'});

    // let instance = new TableExport(selector, {
    //     formats: ['xlsx'],
    //     exportButtons: false,
    //     filename: filename + '-' + date,
    // });
    // let data = instance.getExportData();
    // let exportData = data[Object.keys(data)[0]]['xlsx'];

    // instance.export2file(exportData.data, exportData.mimeType, exportData.filename, exportData.fileExtension);
}