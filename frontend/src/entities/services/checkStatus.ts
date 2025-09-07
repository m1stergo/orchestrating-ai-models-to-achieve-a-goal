type options = {
    interval?: number,
    maxRetries?: number
}
export function checkStatus(checkStatusFn: Function, options?: options) {
    const interval = options?.interval || 2000;
    const maxRetries = options?.maxRetries || 20;
    return new Promise((resolve, reject) => { 
        let retries = 0;
        const retry = async () => {
          console.log("REVISA");
          if (retries >= maxRetries) {
            reject(new Error("Service not available"));
            return;
          }
          try {
            // Ensure we unwrap the computed value to avoid circular references
            const statusResult = await checkStatusFn();
            console.log("statusResult", statusResult);

            // if COMPLETED resolve
            if (statusResult?.status === "COMPLETED") {
                // revisar estado interno para ver si statusResult.output.status === "success"
                if (statusResult?.details?.status === "IDLE") {
                    resolve(true);
                }
                else {
                  setTimeout(retry, interval);
                  retries++;
                }
            } else {
                setTimeout(retry, interval);
                retries++;
            }
          } catch (error: any) {
            console.error('Error checking service status:', error);
            // retries++;
            // if (retries >= maxRetries) {
            //   error.value = error.message
            //   isLoading.value = false
            //   reject(error);
            //   return;
            // }
            // setTimeout(retry, interval);
          }
        };
        
        // Iniciar el proceso de verificación
        retry();
      });
    
}