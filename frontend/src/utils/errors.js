export function getErrorMessage(error, fallback = "Something went wrong") {
  const data = error?.response?.data;
  if (data?.error?.message) {
    return data.error.message;
  }
  if (typeof data?.detail === "string") {
    return data.detail;
  }
  if (error?.message === "Network Error" || error?.code === "ERR_NETWORK") {
    return "Network failure. Check the API URL and that the backend is running.";
  }
  if (error?.message) {
    return error.message;
  }
  return fallback;
}

export function getErrorCode(error) {
  return error?.response?.data?.error?.code || null;
}

export function isUnauthorized(error) {
  return error?.response?.status === 401;
}
