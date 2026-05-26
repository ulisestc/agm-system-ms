const eventConsumer = require('./consumers/event.consumer');

async function main() {
    console.log("=================================================");
    console.log("   Microservicio de Notificaciones Modularizado  ");
    console.log("   Integrado con ms-auth (RPC Auth)            ");
    console.log("=================================================");
    
    await eventConsumer.start();
}

main().catch(err => {
    console.error("Error fatal en el inicio:", err);
    process.exit(1);
});
