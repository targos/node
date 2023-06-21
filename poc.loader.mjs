export function initialize({ entryPoint, port }) {
    console.log('initialize loader', { entryPoint });
    port.postMessage('loader initialized');
}
