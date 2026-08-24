import {api} from './api'

const httpBase = api.defaults.baseURL;

const wsBase = httpBase.replace(/^http/, "ws");

export function createJobWebSocket({
  onMessage,
  onOpen,
  onClose,
  onError,
}) {
//   const protocol =
//     window.location.protocol === "https:"
//       ? "wss:"
//       : "ws:";

//   const socket = new WebSocket(
//     `${protocol}//${window.location.host}/api/v1/jobs/ws`
//   );

   const socket = new WebSocket(
        `${wsBase}/api/v1/jobs/ws` 
    );

  socket.onopen = onOpen;

  socket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      onMessage(message);
    } catch (error) {
      console.error(
        "Invalid WebSocket message:",
        error,
      );
    }
  };

  socket.onclose = onClose;
  socket.onerror = onError;

  return socket;
}