import { useEffect, useRef } from "react";
import { createJobWebSocket } from "../services/jobWebSocket";

export function useJobWebSocket(onJobUpdate) {
  const callbackRef = useRef(onJobUpdate);

  // Always keep the latest callback without recreating the WebSocket.
  useEffect(() => {
    callbackRef.current = onJobUpdate;
  }, [onJobUpdate]);

  useEffect(() => {
    let socket = null;
    let reconnectTimer = null;
    let stopped = false;

    const clearReconnectTimer = () => {
      if (reconnectTimer !== null) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
    };

    const disconnect = () => {
      clearReconnectTimer();

      if (!socket) {
        return;
      }

      // Prevent intentional cleanup from triggering reconnect logic.
      const currentSocket = socket;
      socket = null;

      currentSocket.close();
    };

    const scheduleReconnect = () => {
      if (stopped || reconnectTimer !== null) {
        return;
      }

      reconnectTimer = setTimeout(() => {
        reconnectTimer = null;

        if (!stopped) {
          connect();
        }
      }, 2000);
    };

    const connect = () => {
      if (stopped) {
        return;
      }

      // Don't create multiple sockets.
      if (
        socket &&
        (
          socket.readyState === WebSocket.CONNECTING ||
          socket.readyState === WebSocket.OPEN
        )
      ) {
        return;
      }

      socket = createJobWebSocket({
        onOpen: () => {
          if (stopped) {
            return;
          }

          console.log("JOB WS CONNECTED");
        },

        onMessage: (message) => {
          if (stopped) {
            return;
          }

          if (
            message?.event === "job.created" ||
            message?.event === "job.updated"
          ) {
            callbackRef.current?.(message.job);
          }
        },

        onClose: () => {
          if (stopped) {
            return;
          }

          console.log("JOB WS DISCONNECTED");

          socket = null;
          scheduleReconnect();
        },

        onError: (error) => {
          if (stopped) {
            return;
          }

          console.error("JOB WS ERROR", error);
        },
      });
    };

    connect();

    return () => {
      stopped = true;

      clearReconnectTimer();

      if (socket) {
        const currentSocket = socket;
        socket = null;

        // Detach handlers so React StrictMode cleanup
        // cannot trigger reconnect/error logging.
        currentSocket.onopen = null;
        currentSocket.onmessage = null;
        currentSocket.onerror = null;
        currentSocket.onclose = null;

        if (
          currentSocket.readyState === WebSocket.CONNECTING ||
          currentSocket.readyState === WebSocket.OPEN
        ) {
          currentSocket.close();
        }
      }
    };
  }, []);
}