import System.IO
import Network.Socket
import Network.Socket.ByteString (recv, sendAll)
import qualified Data.ByteString.Char8 as BS
import Control.Exception (try, SomeException)
import Data.List (isPrefixOf, intercalate)

main :: IO ()
main = do
    sock <- socket AF_INET Stream 0
    setSocketOption sock ReuseAddr 1
    bind sock (SockAddrInet 4444 0)
    listen sock 5
    putStrLn "Listening on :4444"
    loop sock

loop :: Socket -> IO ()
loop sock = do
    (conn, _) <- accept sock
    req <- fmap BS.unpack $ recv conn 4096
    let path = extractPath req
    result <- try (readFile path) :: IO (Either SomeException String)
    let body = case result of
                 Left err -> "Erro: " ++ show err
                 Right c  -> c
    let response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" ++ body
    sendAll conn (BS.pack response)
    close conn
    loop sock

extractPath :: String -> FilePath
extractPath req =
    let firstLine = head (lines req)
        parts = words firstLine
        urlPath = if length parts >= 2 then parts !! 1 else "/"
    in urlPath
