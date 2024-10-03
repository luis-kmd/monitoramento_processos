CREATE TABLE HorasTrabalhadas (
    id INT IDENTITY(1,1) PRIMARY KEY,     
    Usuario VARCHAR(255) NOT NULL,      
    Data DATE NOT NULL,                    
    Processo VARCHAR(255) NOT NULL,    
    TempodeAtividade FLOAT NOT NULL,
    TempodeAtividadeFormatado VARCHAR(255),
    SegundosManha FLOAT NULL, 
    SegundosTarde FLOAT NULL, 
    SegundosNoite FLOAT NULL,
    UNIQUE(Usuario, Data)
);

/* CRIAÇAO DA TABELA NO BANCO DE DADOS
OBS: TempodeAtividadeFormatado sera abastecido por uma trigger que esta nesse repositorio.
*/
