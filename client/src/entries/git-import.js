import React from 'react';
import { render } from 'react-dom';
import GitImporter from '../components/git-importer';


render(
    <GitImporter />,
    document.getElementById('mountpoint')
);
