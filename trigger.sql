CREATE TRIGGER tr_ConvertToTimeFormat
ON HorasProcessos
AFTER INSERT, UPDATE
AS
BEGIN
    -- Declara as variáveis
    DECLARE @Usuario VARCHAR(255), @Data DATE, @TempodeAtividade INT;
    
    -- Pega os dados inseridos/atualizados
    SELECT @Usuario = Usuario, @Data = Data, @TempodeAtividade = TempodeAtividade
    FROM inserted;

    -- Converte o tempo de segundos para horas, minutos e segundos
    DECLARE @Horas INT, @Minutos INT, @Segundos INT;
    
    SET @Horas = @TempodeAtividade / 3600;
    SET @Minutos = (@TempodeAtividade % 3600) / 60;
    SET @Segundos = @TempodeAtividade % 60;
    
    -- Atualiza o campo formatado
    UPDATE HorasTrabalhadas
    SET TempodeAtividadeFormatado = FORMAT(@Horas, '00') + ':' + FORMAT(@Minutos, '00') + ':' + FORMAT(@Segundos, '00')
    WHERE Usuario = @Usuario AND Data = @Data;
END;
