import React, { useState, useMemo,useEffect, useCallback, forwardRef } from 'react';
import axios from 'axios';
import './App.css';
import Container from '@mui/material/Container';
import { TextField, Button, Box, InputLabel, Select, MenuItem } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles'; // ✅ Correct import
import ReactMarkdown from 'react-markdown'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// You can import a theme of your choice, e.g.:
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { SimpleTreeView } from '@mui/x-tree-view/SimpleTreeView';
import { TreeItem } from '@mui/x-tree-view/TreeItem';

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

import Typography from '@mui/material/Typography';
import { AiOutlineFolder, AiOutlineFile, AiOutlineFileText, AiOutlineCode, AiOutlineSetting } from 'react-icons/ai';
import { MdOutlineImage } from 'react-icons/md';
import { SiPython, SiDocker, SiJavascript, SiTypescript, SiReact } from 'react-icons/si';

import { FixedSizeList } from 'react-window';
import { useRef } from 'react';

import Autocomplete from '@mui/material/Autocomplete';
import ListSubheader from '@mui/material/ListSubheader';
import { VariableSizeList } from 'react-window'; // for better flexibility
import { useTheme } from '@mui/material/styles';





// ✅ Create theme using createTheme()
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#ef6b38',
    },
    secondary: {
      main: '#38bbef',
    }, 
    error: {
      main: '#ef3860',
    },
    warning: {
      main: '#efc738',
    },
  },
});
const LISTBOX_PADDING = 8; // px

function renderRow(props) {
  const { data, index, style } = props;
  const dataSet = data[index];
  const itemProps = dataSet[0];  // <li> props
    const label = dataSet[1];      // Label/text content
  return (
    <li {...itemProps} style={{ ...style, top: style.top + LISTBOX_PADDING }}>
      {label}
    </li>
  );
}

const ListboxComponent = React.forwardRef(function ListboxComponent(props, ref) {
  const { children, ...other } = props;
  const itemData = [];

  React.Children.forEach(children, (child) => {
    itemData.push([child.props, child.props.children]);
  });

  const itemCount = itemData.length;
  const itemSize = 36;

  const gridRef = useRef();

  return (
    <div ref={ref} {...other}>
      <FixedSizeList
        height={Math.min(8, itemCount) * itemSize + 2 * LISTBOX_PADDING}
        width="100%"
        ref={gridRef}
        outerElementType={React.forwardRef((props, ref) => <ul {...props} ref={ref} />)}
        innerElementType="ul"
        itemData={itemData}
        itemSize={itemSize}
        overscanCount={5}
        itemCount={itemCount}
      >
        {renderRow}
      </FixedSizeList>
    </div>
  );
});

// Fix useResetCache
function useResetCache(dataLength) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current != null) {
      ref.current.resetAfterIndex(0, true);
    }
  }, [dataLength]);
  return ref;
}




function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [chunkCount, setChunkCount] = useState('');
  const [usedChunks, setUsedChunks] = useState();
  const [loading, setLoading] = useState(false);
  const [questionAsked, SetQuestionAsked] = useState('')
  const [repoTree, setRepoTree] = useState([]);
  const memoizedTree = useMemo(() => buildTreeFromPaths(repoTree), [repoTree]);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  const handleFetchFiles = async () => {
    try {
      const [_, owner, repo] = repoUrl.split('/').slice(-3);
      const res = await axios.post(`${API_BASE}/fetch-files`, {
        owner,
        repo,
      });
      setFiles(res.data.files);
      setRepoTree(res.data.repoTree);
      setSelectedFile('')
      setAnswer('')
      toast.success("Repo File Tree is received!");
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  const handleAsk = async () => {
    setLoading(true);
    try {
      const [_, owner, repo] = repoUrl.split('/').slice(-3);
      const res = await axios.post(`${API_BASE}/ask`, {
        owner,
        repo,
        filePath: selectedFile,
        question,
      });
      setAnswer(res.data.answer);
      setChunkCount(res.data.chunk_count);
      setUsedChunks(res.data.used_chunks);
    } catch (error) {
      console.error('Error asking question:', error);
    } finally {
      setLoading(false);
    }
  };
  

  function buildTreeFromPaths(paths) {
    const root = {};
  
    paths.forEach((path) => {
      const parts = path.split('/');
      let current = root;
  
      parts.forEach((part, index) => {
        if (!current[part]) {
          current[part] = {
            __path: parts.slice(0, index + 1).join('/'),
            __children: {},
          };
        }
        current = current[part].__children;
      });
    });
  
    function getFileIcon(fileName) {
      const knownFiles = {
        dockerfile: <SiDocker size={20} />,
        makefile: <AiOutlineSetting size={20} />,
        'readme.md': <AiOutlineFileText size={20} />,
        '.gitignore': <AiOutlineSetting size={20} />,
      };
    
      const lowerName = fileName.toLowerCase();
    
      // Handle known extensionless files
      if (knownFiles[lowerName]) return knownFiles[lowerName];
    
      const extMatch = fileName.match(/\.([^.]+)$/);
      const ext = extMatch ? extMatch[1].toLowerCase() : null;
  
      switch (ext) {
        case null:
          return <AiOutlineFolder  size={24}/>;
        case 'js':
          return <SiJavascript />;
        case 'ts':
          return <SiTypescript />;
        case 'jsx':
          return <SiReact />;
        case 'tsx':
          return <SiReact />;
        case 'json':
          return <AiOutlineCode />;
        case 'md':
        case 'txt':
          return <AiOutlineFileText />;
        case 'py':
          return <SiPython />;
        case 'yml':
        case 'yaml':
          return <AiOutlineSetting />;
        case 'png':
        case 'jpg':
        case 'jpeg':
        case 'gif':
        case 'svg':
          return <MdOutlineImage />;
        default:
          return <AiOutlineFile />;
      }
    }
  
    function renderTree(node) {
      return Object.entries(node).map(([key, value]) => {
        const id = value.__path;
        const isLeaf = Object.keys(value.__children).length === 0;
  
        const icon = isLeaf ? getFileIcon(key) : <AiOutlineFolder />;
  
        return (
          <TreeItem
            key={id}
            itemId={id}
            sx={{ marginBottom: 1 }}
            onClick={() => handleSelectedTreeFile(id, key, isLeaf)}
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {icon}
                <Typography variant="body2">{key}</Typography>
              </Box>
            }
          >
            {!isLeaf && renderTree(value.__children)}
          </TreeItem>
        );
      });
    }
  
    return renderTree(root);
  }

  function handleSelectedTreeFile(path, file, isLeaf) {
    const extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.md', '.cpp', '.h'];
  
    if (!isLeaf) return;
  
    const isSupported = extensions.some(ext => file.endsWith(ext));
    const isInFiles = files.includes(path); // 👈 check against the filtered list
    
    // Debugging logs
    console.log("Selected:", path);
    console.log("In files?", files.includes(path));
    console.log("Available files:", files);
  
    if (isSupported && isInFiles) {
      setSelectedFile(path);
    } else if (!isInFiles) {
      toast.warning('File is not supported or not available for selection.');
    } else {
      toast.warning('Supported file types: .py, .js, .jsx, .ts, .tsx, .md, .cpp, .h');
    }
  }

  

  return (
    <ThemeProvider theme={theme}>
      <Container
        className="container"
        maxWidth={false}
        disableGutters
        sx={{
          height: '100vh',
          bgcolor: 'ThreeDDarkShadow',
          p: {
            sx:0,
            md:2
          },
          // height: {
          //   xs: '100%',
          //   sm: '100vh',
          //   md: '100vh',
          // },
          display: 'flex',
          justifyContent: 'space-between',
          flexDirection: { xs: 'column', md: 'row' },
        }}
      >
        <Container className="main" sx={{ flex: 7, bgcolor: 'white',height:'100%' }} disableGutters>
          <header>
            <h3>Repo Whisperer</h3>
              <TextField 
                id="standard-basic" variant="standard" 
                InputProps={{ disableUnderline: true }} 
                placeholder="Repository URL"
                sx={{ width:'60%', height:'80%',px:2, borderRadius:2,bgcolor:'#f4f4f4', justifyContent:'center'}}
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
              />
            <Button variant="contained" size='large' sx={{ textTransform: 'none' }} onClick={handleFetchFiles}>Fetch Tree</Button>
          </header>
          <Box sx={{
            bgcolor:'', height:'calc(100% - 7vh)', minHeight:'90vh', p:{xs:1,sm:2,md:4}, 
            display:'flex', flexDirection:'column', justifyContent:'space-between', alignItems:'center'
          }}>
            
            <Box className='answer-box' sx={{
              width:'100%',
              height:'85%',
              bgcolor:'#f4f4f4',
              borderRadius:2,
              p:{xs:2,sm:2,md:3},
              overflow:'hidden',
              display:'flex', flexDirection:'column', justifyContent:'space-between'
            }}>
              <div
                className="answer"
                style={{
                  height:'80%',
                  wordWrap: 'break-word',
                  overflowWrap: 'break-word',
                  whiteSpace: 'pre-wrap', // this is often the key one!
                  wordBreak: 'break-word',  
                  padding: '2rem',
                  paddingLeft:'4rem'
                }}
              >
                {answer && <h2 style={{ color: 'black', marginBottom: '1.5rem', backgroundColor: '#f4f4f4', padding: '.3rem', paddingLeft: '1rem', borderRadius: '10px' }}>❝ {questionAsked} ❞</h2>}
                <ReactMarkdown
                  components={{
                    code({node, inline, className, children, ...props}) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={oneDark}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      )
                    }
                  }}
                >
                  {answer}
                </ReactMarkdown>
              </div>
              
              <Box className='file-details' sx={{display:'flex', flexDirection:{xs:'column', sm:'row'},alignItems:'center', justifyContent:'space-between', px:4}}>
                <p className='chuck-count' >Total Chucks : {chunkCount} </p>
                <span className='selector'>
                  
                  {/* Old select */}
                  {/* <Select
                    id="select-file-input"
                    renderValue={() => ''} 
                    onChange={(e) => setSelectedFile(e.target.value)}
                    sx={{
                      width:'40px', height:'40px', textAlign:'center',
                    }}
                  >
                    {files.map((f) => (
                      <MenuItem key={f} value={f}>
                        {f}
                      </MenuItem>
                    ))}
                  </Select> */}

                  {/* Slection with react-windo */}
                  <Autocomplete
                    id="virtualized-autocomplete"
                    disableListWrap
                    ListboxComponent={ListboxComponent}
                    options={files}
                    value={selectedFile || null}
                    onChange={(event, newValue) => {
                      setSelectedFile(newValue || '');
                    }}
                    sx={{
                        width: {
                          xs: '100%',  // Full width on small screens
                          sm: '80%',
                          md: 400,     // Fixed width on medium and up
                        },
                        textAlign: 'end',
                        borderColor:'red'
                      }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        variant="outlined"
                        placeholder="Select a file"
                        fullWidth
                      />
                    )}
                    renderOption={(props, option) => {
                      const { key, ...rest } = props;
                      return (
                        <li key={key} {...rest}>
                          {option}
                        </li>
                      );
                    }}

                  />

                </span>                
              </Box>            
            </Box>
            
            {/* The Input for Questions */}
            <Box sx={{width:'100%',textAlign:'center',marginBottom:2, display:'flex', justifyContent:'center', alignItems:'center'}}>
              <TextField 
                id="standard-basic" variant="standard" 
                InputProps={{ disableUnderline: true }} 
                
                sx={{ width:'60%',p:1.5, borderRadius:2, mx:1, bgcolor:'#f4f4f4'}}
                placeholder='Enter your question'
                value={question}
                onChange={(e) => {setQuestion(e.target.value)}}
              />
              <Button variant="contained" sx={{ textTransform: 'none', p:1.5 }} onClick={() => {
                    if (!question.trim()) {
                      toast.warn("Please enter a question first!");
                      return;
                    }
                    if (!selectedFile) {
                      toast.warn("Please select a file");
                      return;
                    }
                    handleAsk();
                    SetQuestionAsked(question);
                    setQuestion('');
                    setAnswer(''); 
                    
                  }}>Ask</Button>
            </Box>
          </Box>
          
        </Container>
        
        <Container className="sidebar" sx={{ flex:3, bgcolor:'#f4f4f4'}} disableGutters>
          <header><h3>File Struture</h3>  </header>
          <SimpleTreeView
            aria-label="repo file system navigator"
            slots={{
              expandIcon: ExpandMoreIcon,
              collapseIcon: ChevronRightIcon,
            }}
            sx={{ overflowY: 'auto', p: 2, height: 'calc(100% - 48px)', overflowX:'scroll'}}
          >
            {memoizedTree}
          </SimpleTreeView>
        </Container>
        
      </Container>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={true}
        closeOnClick
        pauseOnHover
        draggable
      />
    </ThemeProvider>
  );
}

export default App;
