import React from "react";
import dayjs from "dayjs";
import "./Site.css";

function getRatioColor(ratio) {
    if (ratio <= 0.5) return "Red";
    else if (ratio <= 0.75) return "Orange";
    else if (ratio < 1) return "Yellow";
    else if (ratio == 1) return "Green";
    else return "White";
}

const Site = (props) => {
    const data = props.data;
    const history = [];
    const formatString = "YYYY-MM-DD";

    const last30Days = {};
    for (let i = 0; i < 30; i++) {
        last30Days[dayjs().subtract(i, "day").format(formatString)] = [];
    }
    data.history.forEach((element) => {
        last30Days[dayjs(element.time).format(formatString)].push(element.up);
    });

    const last30Ratio = [];
    for (let i = 29; i >= 0; i--) {
        const date = dayjs().subtract(i, "day").format(formatString);
        const day = last30Days[date];
        let good = day.filter((item) => item == true).length;
        last30Ratio.push({ day: date, ratio: good / day.length });
    }

    console.log(last30Ratio);
    return (
        <div className="Site">
            <h2>{data.name}</h2>
            <div className="ThirtyDays">
                {last30Ratio.map((day) => (
                    <span className={"SingleDay " + getRatioColor(day.ratio)}></span>
                ))}
            </div>
        </div>
    );
};

export default Site;
