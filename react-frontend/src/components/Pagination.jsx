import React from 'react'

export default function Pagination ({currentPage, pageList, paginate}) {
    const pageNumbers = [];

    return (
        <tfoot>
            <tr><th colspan="5">
                <div class="ui right floated pagination menu">
                    <a class="icon item">
                        <i class="left chevron icon"></i>
                    </a>
                    {pageList.map(number => <a onClick={() => paginate({number})} class="item">{number}</a>)}
                    <a class="icon item">
                        <i class="right chevron icon"></i>
                    </a>
                </div>
            </th>
            </tr>
        </tfoot>
    )
}

