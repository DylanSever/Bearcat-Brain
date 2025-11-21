import { Link } from "react-router-dom";

const NotFoundPage = () => {
    return (
        <div>
            <h2>Page Not Found</h2>
            <Link to={"/"}>
                <button>Go back Home</button>
            </Link>
        </div>
    );
};

export default NotFoundPage