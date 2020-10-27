import React from "react";

const Site = (props) => {
    const data = props.data;

    return (
        <div className="site">
            <h2>{data.name}</h2>
        </div>
    );
};

export default Site;
