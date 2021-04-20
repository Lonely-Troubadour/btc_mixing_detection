import React from 'react'
import { useTable } from 'react-table'
import Pagination from './Pagination'

export default function Tabel({ columns, data, pageList, paginate }) {
    return (
        <div class="scrolling content">
            <table class="ui celled stackable compact table ">
                <thead>
                    <tr>{columns.map(column => <th>{column}</th>)}
                        {/* <th class="single line">Id</th>
                    <th>Hash</th>
                    <th>Height</th>
                    <th>Time</th> */}
                        {/* <th>Type</th> */}
                    </tr>
                </thead>
                <tbody>
                    {data.map(row => <tr>
                        {row.map(column => <td>{column}</td>)}
                    </tr>)}
                </tbody>
                <Pagination pageList={pageList} paginate={paginate}/>
            </table>
        </div>
    )
}
