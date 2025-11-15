// Root layout used for shared UI across all pages.
// Empty now, but here to add shared UI if needed without changing routes.

import { Outlet } from "react-router-dom";

function Root() {
    return (
        <div className="root-wrapper">
            <Outlet />
        </div>
    );
}

export default Root;
