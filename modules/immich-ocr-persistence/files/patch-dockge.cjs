// Extend only the existing authenticated stack Update action.
const fs=require('node:fs'),p='/app/backend/stack.ts',marker='// immich-maintenance-v1';
const src=fs.readFileSync(p,'utf8');
const anchor='    async update(socket: DockgeSocket) {';
if(!src.includes(marker)){
 if(src.split(anchor).length!==2)throw Error('Dockge incompatible : méthode update inconnue');
 const addition=`
        ${marker}
        if (fs.existsSync(path.join(this.path, "ocr-hook", "update-nas.cjs"))) {
            const name = getComposeTerminalName(socket.endpoint, this.name);
            const code = await Terminal.exec(this.server, socket, name, "flock",
                [ "-n", ".immich-update.lock", "node", "ocr-hook/update-nas.cjs" ], this.path);
            if (code !== 0) { throw new Error("Mise à jour Immich interrompue : voir le terminal."); }
            return code;
        }
`;
 fs.writeFileSync(p,src.replace(anchor,anchor+addition));
}
console.log('Dockge : action de mise à jour Immich installée.');
