function execute_task(path){
    $.ajax({
       type: 'GET',
       url: 'execute_task/',
       data: {
           'path': path
       }
    })
};