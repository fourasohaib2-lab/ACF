interface Props { caption: string; columns: string[]; rows: (string | number)[][] }

/** Accessible alternative to a chart: the exact values it draws. */
export const DataTable = ({ caption, columns, rows }: Props) => (
  <table className="data-table">
    <caption className="visually-hidden">{caption}</caption>
    <thead><tr>{columns.map((c) => <th key={c} scope="col">{c}</th>)}</tr></thead>
    <tbody>{rows.map((r, i) => <tr key={i}>{r.map((v, j) => <td key={j}>{v}</td>)}</tr>)}</tbody>
  </table>
);
