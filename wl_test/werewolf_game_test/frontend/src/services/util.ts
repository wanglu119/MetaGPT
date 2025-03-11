
const GetNkHostname = ()=>{
    let host = ''
    if(process.env.NODE_ENV ==="development") {
        host = `${process.env.VUE_APP_SERVER_NK_HOST}`
    } else {
        host = document.location.origin
    }
    return host
}


const GetApiHostname = ()=>{
    let host = ''
    if(process.env.NODE_ENV ==="development") {
        host = `${process.env.VUE_APP_SERVER_API_HOST}`
    } else {
        host = document.location.origin
    }
    return host
}

const UtilApi = {
    GetNkHostname,
    GetApiHostname,
  }
  
  export default UtilApi
  